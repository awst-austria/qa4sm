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
from validator.validation import run_validation, globals
from validator.validation.validation import compare_validation_runs


def _check_if_settings_exist():
    pass


@api_view(['GET'])
@permission_classes([AllowAny])
def get_scaling_methods(request):
    scaling_methods = [{'method': x, 'description': y} for x, y in globals.SCALING_METHODS]
    return JsonResponse(scaling_methods, status=status.HTTP_200_OK, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_validation(request):
    check_for_existing_validation = request.query_params.get('check_for_existing_validation', False)

    ser = ValidationConfigurationSerializer(data=request.data)
    try:
        ser.is_valid(raise_exception=True)
    except:
        print(ser.errors)
        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

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
        'variables': [],
        'versions': [],
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

        # temporal matching window:
        val_run_dict['temporal_matching'] = val_run.temporal_matching

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

        if val_run.anomalies_to is not None:
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

        # if one day we decide to remove any of these metrics, we need to check if reloaded settings use them
        metrics = [{'id': 'tcol', 'value': val_run.tcol},
                   {'id': 'bootstrap_tcol_cis', 'value': val_run.bootstrap_tcol_cis},
                   {'id': 'stability_metrics', 'value': val_run.stability_metrics}]
        val_run_dict['metrics'] = metrics

        val_run_dict['intra_annual_metrics'] = \
            {'intra_annual_metrics': val_run.intra_annual_metrics, 'intra_annual_type': val_run.intra_annual_type,
             'intra_annual_overlap': val_run.intra_annual_overlap}

        # dataset configs and filters
        datasets = []
        val_run_dict['dataset_configs'] = datasets

        for ds in validation_configs:

            dataset_id = ds.dataset.id
            version_id = ds.version_id
            variable_id = ds.variable_id

            # We can use get, because if the dataset or the version doesn't exist in our db, the code above handles it.
            dataset = Dataset.objects.get(pk=dataset_id)
            version = DatasetVersion.objects.get(pk=version_id)

            dataset_versions = dataset.versions.all()
            version_variables = version.variables.all()

            # we are checking if the version and variable is still assigned to the dataset:
            variable_assigned = DataVariable.objects.get(pk=variable_id) in version_variables
            version_assigned = DatasetVersion.objects.get(pk=version_id) in dataset_versions

            if not variable_assigned:
                changes_in_settings['variables'].append(
                    {'variable': DataVariable.objects.get(pk=variable_id).pretty_name,
                     'dataset': dataset.pretty_name}
                )
                variable_id = max(version_variables.values_list('id', flat=True))
            if not version_assigned:
                changes_in_settings['versions'].append({
                    'version': DatasetVersion.objects.get(pk=version_id).pretty_name,
                    'dataset': dataset.pretty_name
                })
                version_id = max(dataset_versions.values_list('id', flat=True))

            ds_dict = {'dataset_id': dataset_id,
                       'version_id': version_id,
                       'variable_id': variable_id,
                       'is_spatial_reference': ds.is_spatial_reference,
                       'is_temporal_reference': ds.is_temporal_reference,
                       'is_scaling_reference': ds.is_scaling_reference}
            filters_list = []
            non_existing_filters_list = []
            ds_dict['basic_filters'] = filters_list

            for basic_filter in ds.filters.all():
                # check if the reloaded filter still belongs to the dataset
                datasetversion_filters = DatasetVersion.objects.get(id=version_id).filters.all()
                if basic_filter in datasetversion_filters:
                    filters_list.append(basic_filter.id)
                else:
                    non_existing_filters_list.append(basic_filter.description)

            parametrised_filters = []
            ds_dict['parametrised_filters'] = parametrised_filters
            for param_filter in ParametrisedFilter.objects.filter(dataset_config=ds):
                # check if the reloaded filter still belongs to the dataset
                datasetversion_filter_ids = DatasetVersion.objects.get(id=version_id).filters.all().values_list('id',
                                                                                                                   flat=True)
                if param_filter.filter_id in datasetversion_filter_ids:
                    parametrised_filters.append({'id': param_filter.filter.id, 'parameters': param_filter.parameters})
                else:
                    filter_desc = DataFilter.objects.get(id=param_filter.filter.id).description
                    non_existing_filters_list.append(filter_desc)

            if len(non_existing_filters_list) != 0:
                changes_in_settings['filters'].append(
                    {'dataset': ds.dataset.pretty_name, 'filter_desc': non_existing_filters_list})

            datasets.append(ds_dict)

        if (changes_in_settings['anomalies'] or changes_in_settings['scaling']
                or len(changes_in_settings['filters']) != 0
                or len(changes_in_settings['variables']) != 0
                or len(changes_in_settings['versions']) != 0):
            val_run_dict['changes'] = True

        val_run_dict['settings_changes'] = changes_in_settings
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
    is_spatial_reference = serializers.BooleanField(required=True)
    is_temporal_reference = serializers.BooleanField(required=True)
    is_scaling_reference = serializers.BooleanField(required=True)


# Metrics DTO and serializer
class MetricsSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    id = serializers.CharField(required=True)
    value = serializers.BooleanField(required=True)


class IntraAnnualMetricsSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    intra_annual_metrics = serializers.BooleanField(default=False)
    intra_annual_type = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    intra_annual_overlap = serializers.IntegerField(allow_null=True)


class ValidationConfigurationSerializer(serializers.Serializer):
    requires_context = True

    def validate(self, attrs):
        spatial_ref_configs_num = len(list(filter(lambda el: el['is_spatial_reference'], attrs['dataset_configs'])))
        temporal_ref_configs_num = len(list(filter(lambda el: el['is_temporal_reference'], attrs['dataset_configs'])))
        scaling_ref_configs_num = len(list(filter(lambda el: el['is_scaling_reference'], attrs['dataset_configs'])))

        if spatial_ref_configs_num == 0:
            raise serializers.ValidationError('No spatial reference provided.')
        elif spatial_ref_configs_num > 1:
            raise serializers.ValidationError('More than one spatial reference provided.')

        if temporal_ref_configs_num == 0:
            raise serializers.ValidationError('No temporal reference provided.')
        elif temporal_ref_configs_num > 1:
            raise serializers.ValidationError('More than one temporal reference provided.')

        if scaling_ref_configs_num == 0 and attrs['scaling_method'] != 'none':
            raise serializers.ValidationError('No scaling reference provided, but the scaling method is set.')
        elif scaling_ref_configs_num == 1 and attrs['scaling_method'] == 'none':
            raise serializers.ValidationError('Scaling reference set, but the scaling method not.')
        elif scaling_ref_configs_num > 1 and attrs['scaling_method'] != 'none':
            raise serializers.ValidationError('More than one scaling reference provided.')

        return attrs

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
            new_val_run.temporal_matching = validated_data.get('temporal_matching', None)
            new_val_run.intra_annual_metrics = validated_data.get('intra_annual_metrics', None)

            for key, value in validated_data.get('intra_annual_metrics', None).items():
                setattr(new_val_run, key, value)

            for metric in validated_data.get('metrics'):
                setattr(new_val_run, metric.get('id'), metric.get('value'))

            new_val_run.save()

            # prepare DatasetConfiguration models
            reference_config = None
            dataset_config_models = []
            configs_to_save = validated_data.get('dataset_configs')

            spatial_ref_index = configs_to_save.index(
                next(filter(lambda n: n.get('is_spatial_reference'), configs_to_save)))
            configs_to_save.append(configs_to_save.pop(spatial_ref_index))
            # else:
            #     return None

            for config in configs_to_save:
                config_model = DatasetConfiguration.objects.create(validation=new_val_run,
                                                                   dataset_id=config.get('dataset_id'),
                                                                   version_id=config.get('version_id'),
                                                                   variable_id=config.get('variable_id'),
                                                                   is_spatial_reference=config.get(
                                                                       'is_spatial_reference'),
                                                                   is_temporal_reference=config.get(
                                                                       'is_temporal_reference'),
                                                                   is_scaling_reference=config.get(
                                                                       'is_scaling_reference'))
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
                if config_model.is_spatial_reference:
                    new_val_run.spatial_reference_configuration = config_model

                if config_model.is_temporal_reference:
                    new_val_run.temporal_reference_configuration = config_model

                if config_model.is_scaling_reference:
                    new_val_run.scaling_ref = config_model

                dataset_config_models.append(config_model)

            new_val_run.save()

        return new_val_run

    dataset_configs = DatasetConfigSerializer(many=True, required=True)
    interval_from = serializers.DateTimeField(required=False)
    interval_to = serializers.DateTimeField(required=False)
    metrics = MetricsSerializer(many=True, required=True)
    anomalies_method = serializers.ChoiceField(choices=ValidationRun.ANOMALIES_METHODS, required=True)
    anomalies_from = serializers.DateTimeField(required=False, allow_null=True)
    anomalies_to = serializers.DateTimeField(required=False, allow_null=True)
    scaling_method = serializers.ChoiceField(choices=ValidationRun.SCALING_METHODS, required=True)
    min_lat = serializers.FloatField(required=False, allow_null=True, default=-90.0)
    min_lon = serializers.FloatField(required=False, allow_null=True, default=-180)
    max_lat = serializers.FloatField(required=False, allow_null=True, default=90)
    max_lon = serializers.FloatField(required=False, allow_null=True, default=180)
    name_tag = serializers.CharField(required=False, allow_null=True, max_length=80, allow_blank=True)
    temporal_matching = serializers.IntegerField(allow_null=False, default=globals.TEMP_MATCH_WINDOW)
    intra_annual_metrics = IntraAnnualMetricsSerializer(many=False, required=False)


class ValidationConfigurationModelSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(model)
