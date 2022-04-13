from multiprocessing.context import Process

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connections
from django.db.models import Case, When
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer

from api.views.auxiliary_functions import get_fields_as_list
from api.views.validation_run_view import ValidationRunSerializer
from validator.models import ValidationRun, DatasetConfiguration, DataFilter, ParametrisedFilter, Dataset, \
    DatasetVersion, DataVariable
from validator.validation import run_validation
from validator.validation.validation import compare_validation_runs


def _check_if_settings_exist():
    pass


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_validation(request):
    check_for_existing_validation = request.query_params.get('check_for_existing_validation', False)

    ser = ValidationConfigurationSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    new_val_run = ser.save(user=request.user)
    new_val_run.user = request.user
    new_val_run.save()
    # need to close all db connections before forking, see
    # https://stackoverflow.com/questions/8242837/django-multiprocessing-and-database-connections/10684672#10684672

    if check_for_existing_validation == 'true':
        existing_runs = ValidationRun.objects.filter(progress=100).exclude(output_file=''). \
            order_by(Case(When(user=request.user, then=0), default=1), '-start_time')
        comparison_pub = compare_validation_runs(new_val_run, existing_runs, request.user)

        if comparison_pub['is_there_validation']:
            new_val_run.delete()
            response = JsonResponse(comparison_pub, status=status.HTTP_200_OK, safe=False)
            return response

    connections.close_all()
    p = Process(target=run_validation, kwargs={"validation_id": new_val_run.id})
    p.start()
    serializer = ValidationRunSerializer(new_val_run)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_validation_configuration(request, **kwargs):
    changes_in_settings = {
        'filters': [],
        'anomalies': False,
        'scaling': False,
        'variables': []
    }

    validation_run_id = kwargs['id']
    try:
        val_run = ValidationRun.objects.get(pk=validation_run_id)
        validation_configs = val_run.dataset_configurations.all()

        #  first check if there are still all the datasets available:
        datasets_in_validation = validation_configs.values_list('dataset', flat=True)
        ds_versions_in_validation = validation_configs.values_list('version', flat=True)
        ds_variables_in_validation = validation_configs.values_list('variable', flat=True)

        available_datasets = Dataset.objects.all().values_list('id', flat=True)
        available_versions = DatasetVersion.objects.all().values_list('id', flat=True)
        available_variables = DataVariable.objects.all().values_list('id', flat=True)

        all_datasets_available = all([dataset in available_datasets for dataset in datasets_in_validation])
        all_versions_available = all([version in available_versions for version in ds_versions_in_validation])
        all_variables_available = all([variable in available_variables for variable in ds_variables_in_validation])

        if not (all_datasets_available and all_versions_available and all_variables_available):
            return JsonResponse({'message': 'Could not restore validation run, because some of '
                                            'the chosen datasets, their versions or variables are not available anymore'},
                                status=status.HTTP_404_NOT_FOUND, safe=False)

        val_run_dict = {'name_tag': val_run.name_tag}

        if val_run.interval_from is not None:
            val_run_dict['interval_from'] = val_run.interval_from.date()
        else:
            val_run_dict['interval_from'] = None

        if val_run.interval_to is not None:
            val_run_dict['interval_to'] = val_run.interval_to.date()
        else:
            val_run_dict['interval_to'] = None

        # if the anomaly method doesn't exist anymore, set 'none'
        if val_run.anomalies is not None and val_run.anomalies in dict(ValidationRun.ANOMALIES_METHODS).keys():
            val_run_dict['anomalies_method'] = val_run.anomalies
        else:
            val_run_dict['anomalies_method'] = ValidationRun.NO_ANOM
            changes_in_settings['anomalies'] = True

        if val_run.anomalies_from is not None:
            val_run_dict['anomalies_from'] = val_run.anomalies_from.date()
        else:
            val_run_dict['anomalies_from'] = None

        if val_run.anomalies_from is not None:
            val_run_dict['anomalies_to'] = val_run.anomalies_to.date()
        else:
            val_run_dict['anomalies_to'] = None

        val_run_dict['min_lat'] = val_run.min_lat
        val_run_dict['min_lon'] = val_run.min_lon
        val_run_dict['max_lat'] = val_run.max_lat
        val_run_dict['max_lon'] = val_run.max_lon

        # if a scaling method doesn't exist anymore, set 'none'
        if val_run.scaling_method in dict(ValidationRun.SCALING_METHODS).keys():
            val_run_dict['scaling_method'] = val_run.scaling_method
        else:
            val_run_dict['scaling_method'] = ValidationRun.NO_SCALING
            changes_in_settings['scaling'] = True

        if val_run.scaling_method is not None or val_run.scaling_method != 'none':
            val_run_dict['scale_to'] = ValidationRun.SCALE_TO_REF
            if val_run.scaling_ref is not None:
                if val_run.scaling_ref.id != val_run.reference_configuration.id:
                    val_run_dict['scale_to'] = ValidationRun.SCALE_TO_DATA

        # if one day we decide to remove any of these metrics, we need to check if reloaded settings use them
        metrics = [{'id': 'tcol', 'value': val_run.tcol},
                   {'id': 'bootstrap_tcol_cis', 'value': val_run.bootstrap_tcol_cis}]
        val_run_dict['metrics'] = metrics

        # dataset configs and filters
        datasets = []
        val_run_dict['dataset_configs'] = datasets

        for ds in validation_configs:

            dataset_id = ds.dataset.id

            if ds.variable_id not in Dataset.objects.get(pk=dataset_id).variables.all():
                return JsonResponse({'message': 'Could not restore validation run, because some of '
                                                'the chosen datasets, their versions or variables '
                                                'are not available anymore'},
                                    status=status.HTTP_404_NOT_FOUND, safe=False)

            ds_dict = {'dataset_id': dataset_id, 'version_id': ds.version_id, 'variable_id': ds.variable_id}
            filters_list = []
            non_existing_filters_list = []
            ds_dict['basic_filters'] = filters_list

            for basic_filter in ds.filters.all():
                # check if the reloaded filter still belongs to the dataset
                dataset_filters = Dataset.objects.get(id=dataset_id).filters.all()
                if basic_filter in dataset_filters:
                    filters_list.append(basic_filter.id)
                else:
                    non_existing_filters_list.append(basic_filter.description)

            parametrised_filters = []
            ds_dict['parametrised_filters'] = parametrised_filters
            for param_filter in ParametrisedFilter.objects.filter(dataset_config=ds):
                # check if the reloaded filter still belongs to the dataset
                dataset_filter_ids = Dataset.objects.get(id=dataset_id).filters.all().values_list('id', flat=True)
                if param_filter.filter_id in dataset_filter_ids:
                    parametrised_filters.append({'id': param_filter.filter.id, 'parameters': param_filter.parameters})
                else:
                    filter_desc = DataFilter.objects.get(id=param_filter.filter.id).description
                    non_existing_filters_list.append(filter_desc)

            if len(non_existing_filters_list) != 0:
                changes_in_settings['filters'].append(
                    {'dataset': ds.dataset.pretty_name, 'filter_desc': non_existing_filters_list})

            if val_run.reference_configuration_id == ds.id:
                val_run_dict['reference_config'] = {
                    'dataset_id': val_run.reference_configuration.dataset.id,
                    'version_id': val_run.reference_configuration.version.id,
                    'variable_id': val_run.reference_configuration.variable.id,
                    'basic_filters': filters_list,
                    'parametrised_filters': parametrised_filters
                }
            else:
                datasets.append(ds_dict)

        if changes_in_settings['anomalies'] or changes_in_settings['scaling'] or \
                len(changes_in_settings['filters']) != 0:
            val_run_dict['changes'] = changes_in_settings

        return JsonResponse(val_run_dict,
                            status=status.HTTP_200_OK, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse(None, status=status.HTTP_404_NOT_FOUND, safe=False)


class ParameterisedFilterConfigSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    id = serializers.IntegerField(required=True)
    parameters = serializers.CharField(required=True)


class DatasetConfigSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    dataset_id = serializers.IntegerField(required=True)
    version_id = serializers.IntegerField(required=True)
    variable_id = serializers.IntegerField(required=True)
    basic_filters = serializers.ListField(child=serializers.IntegerField(), required=True)
    parametrised_filters = ParameterisedFilterConfigSerializer(many=True)


# Metrics DTO and serializer
class MetricsSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    id = serializers.CharField(required=True)
    value = serializers.BooleanField(required=True)


class ValidationConfigurationSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):

        with transaction.atomic():
            # prepare ValidationRun model
            new_val_run = ValidationRun(start_time=timezone.now())
            new_val_run.interval_from = validated_data.get('interval_from', None)
            new_val_run.interval_to = validated_data.get('interval_to', None)
            new_val_run.anomalies = validated_data.get('anomalies_method')
            new_val_run.anomalies_from = validated_data.get('anomalies_from', None)
            new_val_run.anomalies_to = validated_data.get('anomalies_to', None)
            new_val_run.min_lat = validated_data.get('min_lat', None)
            new_val_run.min_lon = validated_data.get('min_lon', None)
            new_val_run.max_lat = validated_data.get('max_lat', None)
            new_val_run.max_lon = validated_data.get('max_lon', None)
            new_val_run.scaling_method = validated_data.get('scaling_method', None)
            new_val_run.name_tag = validated_data.get('name_tag', None)

            for metric in validated_data.get('metrics'):
                if metric.get('id') == 'tcol':
                    new_val_run.tcol = metric.get('value')
                if metric.get('id') == 'bootstrap_tcol_cis':
                    new_val_run.bootstrap_tcol_cis = metric.get('value')

            new_val_run.save()

            # prepare DatasetConfiguration models
            reference_config = None
            dataset_config_models = []
            configs_to_save = validated_data.get('dataset_configs')
            configs_to_save.append(validated_data.get('reference_config'))
            for config in configs_to_save:
                config_model = DatasetConfiguration.objects.create(validation=new_val_run,
                                                                   dataset_id=config.get('dataset_id'),
                                                                   version_id=config.get('version_id'),
                                                                   variable_id=config.get('variable_id'))
                config_model.save()

                for filter_id in config.get('basic_filters'):
                    config_model.filters.add(DataFilter.objects.get(id=filter_id))

                for param_filter in config.get('parametrised_filters'):
                    param_filter_model = ParametrisedFilter.objects.create(
                        dataset_config=config_model,
                        filter_id=param_filter.get('id'),
                        parameters=param_filter.get('parameters')
                    )
                    param_filter_model.save()

                config_model.save()
                dataset_config_models.append(config_model)

            new_val_run.reference_configuration = dataset_config_models[-1]
            scale_to = validated_data.get('scaling_method', None)
            if scale_to is not None:
                if scale_to == ValidationRun.SCALE_TO_DATA:
                    new_val_run.scaling_ref = dataset_config_models[1]
                else:
                    new_val_run.scaling_ref = dataset_config_models[-1]

            new_val_run.save()

        return new_val_run

    dataset_configs = DatasetConfigSerializer(many=True, required=True)
    reference_config = DatasetConfigSerializer(required=True)
    interval_from = serializers.DateTimeField(required=False)
    interval_to = serializers.DateTimeField(required=False)
    metrics = MetricsSerializer(many=True, required=True)
    anomalies_method = serializers.ChoiceField(choices=ValidationRun.ANOMALIES_METHODS, required=True)
    anomalies_from = serializers.DateTimeField(required=False, allow_null=True)
    anomalies_to = serializers.DateTimeField(required=False, allow_null=True)
    scaling_method = serializers.ChoiceField(choices=ValidationRun.SCALING_METHODS, required=True)
    scale_to = serializers.ChoiceField(choices=ValidationRun.SCALE_TO_OPTIONS, required=True)
    min_lat = serializers.FloatField(required=False, allow_null=True, default=-90.0)
    min_lon = serializers.FloatField(required=False, allow_null=True, default=-180)
    max_lat = serializers.FloatField(required=False, allow_null=True, default=90)
    max_lon = serializers.FloatField(required=False, allow_null=True, default=180)
    name_tag = serializers.CharField(required=False, allow_null=True, max_length=80, allow_blank=True)


class ValidationConfigurationModelSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(model)
