from multiprocessing.context import Process

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connections
from django.http import JsonResponse
from django.utils import timezone
from numpy.testing._private.parameterized import param
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer

from api.views.auxiliary_functions import get_fields_as_list
from api.views.validation_run_view import ValidationRunSerializer
from validator.models import ValidationRun, DatasetConfiguration, DataFilter, ParametrisedFilter
from validator.validation import run_validation
import validator.validation.globals as val_globals
from django.db.models import Case, When

def _compare_param_filters(new_param_filters, old_param_filters):
    """
    Checking if parametrised filters are the same for given configuration, checks till finds the first failure
    or till the end of the list.

    If lengths of queries do not agree then return False.
    """
    if len(new_param_filters) != len(old_param_filters):
        return False
    else:
        ind = 0
        max_ind = len(new_param_filters)
        is_the_same = True
        while ind < max_ind and new_param_filters[ind].parameters == old_param_filters[ind].parameters:
            ind += 1
        if ind != len(new_param_filters):
            is_the_same = False

    return is_the_same


def _compare_filters(new_dataset, old_dataset):
    """
    Checking if filters are the same for given configuration, checks till finds the first failure or till the end
     of the list. If filters are the same, then parameterised filters are checked.

    If lengths of queries do not agree then return False.
    """

    new_run_filters = new_dataset.filters.all().order_by('name')
    old_run_filters = old_dataset.filters.all().order_by('name')
    new_filts_len = len(new_run_filters)
    old_filts_len = len(old_run_filters)

    if new_filts_len != old_filts_len:
        return False
    elif new_filts_len == old_filts_len == 0:
        is_the_same = True
        new_param_filters = new_dataset.parametrisedfilter_set.all().order_by('filter_id')
        if len(new_param_filters) != 0:
            old_param_filters = old_dataset.parametrisedfilter_set.all().order_by('filter_id')
            is_the_same = _compare_param_filters(new_param_filters, old_param_filters)
        return is_the_same
    else:
        filt_ind = 0
        max_filt_ind = new_filts_len

        while filt_ind < max_filt_ind and new_run_filters[filt_ind] == old_run_filters[filt_ind]:
            filt_ind += 1

        if filt_ind == max_filt_ind:
            is_the_same = True
            new_param_filters = new_dataset.parametrisedfilter_set.all().order_by('filter_id')
            if len(new_param_filters) != 0:
                old_param_filters = old_dataset.parametrisedfilter_set.all().order_by('filter_id')
                is_the_same = _compare_param_filters(new_param_filters, old_param_filters)
        else:
            is_the_same = False
    return is_the_same


def _compare_datasets(new_run_config, old_run_config):
    """
    Takes queries of dataset configurations and compare datasets one by one. If names and versions agree,
    checks filters.

    Runs till the first failure or til the end of the configuration list.
    If lengths of queries do not agree then return False.
    """
    new_len = len(new_run_config)

    if len(old_run_config) != new_len:
        return False
    else:
        ds_fields = val_globals.DS_FIELDS
        max_ds_ind = len(ds_fields)
        the_same = True
        conf_ind = 0

        while conf_ind < new_len and the_same:
            ds_ind = 0
            new_dataset = new_run_config[conf_ind]
            old_dataset = old_run_config[conf_ind]
            while ds_ind < max_ds_ind and getattr(new_dataset, ds_fields[ds_ind]) == getattr(old_dataset, ds_fields[ds_ind]):
                ds_ind += 1
            if ds_ind == max_ds_ind:
                the_same = _compare_filters(new_dataset, old_dataset)
            else:
                the_same = False
            conf_ind += 1
    return the_same


def _check_scaling_method(new_run, old_run):
    """
    It takes two validation runs and compares scaling method together with the scaling reference dataset.

    """
    new_run_sm = new_run.scaling_method
    if new_run_sm != old_run.scaling_method:
        return False
    else:
        if new_run_sm != 'none':
            try:
                new_scal_ref = DatasetConfiguration.objects.get(pk=new_run.scaling_ref_id).dataset
                run_scal_ref = DatasetConfiguration.objects.get(pk=old_run.scaling_ref_id).dataset
                if new_scal_ref != run_scal_ref:
                    return False
            except:
                return False
    return True


def _compare_validation_runs(new_run, runs_set, user):
    """
    Compares two validation runs. It takes a new_run and checks the query given by runs_set according to parameters
    given in the vr_fileds. If all fields agree it checks datasets configurations.

    It works till the first found validation run or till the end of the list.

    Returns a dict:
         {
        'is_there_validation': is_the_same,
        'val_id': val_id
        }
        where is_the_same migh be True or False and val_id might be None or the appropriate id ov a validation run
    """
    vr_fields = val_globals.VR_FIELDS
    is_the_same = False # set to False because it looks for the first found validation run
    is_published = False
    old_user = None
    max_vr_ind = len(vr_fields)
    max_run_ind = len(runs_set)
    run_ind = 0
    while not is_the_same and run_ind < max_run_ind:
        run = runs_set[run_ind]
        ind = 0
        while ind < max_vr_ind and getattr(run, vr_fields[ind]) == getattr(new_run, vr_fields[ind]):
            ind += 1
        if ind == max_vr_ind and _check_scaling_method(new_run, run):
            new_run_config = DatasetConfiguration.objects.filter(validation=new_run).order_by('dataset')
            old_run_config = DatasetConfiguration.objects.filter(validation=run).order_by('dataset')
            is_the_same = _compare_datasets(new_run_config, old_run_config)
            val_id = run.id
            is_published = run.doi != ''
            old_user = run.user
        run_ind += 1

    val_id = None if not is_the_same else val_id
    response = {
        'is_there_validation': is_the_same,
        'val_id': val_id,
        'belongs_to_user': old_user == user,
        'is_published': is_published
        }
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_validation(request):
    check_for_existing_validation = request.query_params.get('check_for_existing_validation', None)
    existing_runs = ValidationRun.objects.filter(progress=100).exclude(output_file=''). \
        order_by(Case(When(user=request.user, then=0), default=1), '-start_time')
    ser = ValidationConfigurationSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    new_val_run = ser.save(user=request.user)
    new_val_run.user = request.user
    new_val_run.save()
    comparison_pub = _compare_validation_runs(new_val_run, existing_runs, request.user)
    connections.close_all()
    # print(comparison_pub, comparison_pub['is_there_validation'])
    if check_for_existing_validation == 'true' and comparison_pub['is_there_validation']:
        new_val_run.delete()
        response = JsonResponse(comparison_pub, status=status.HTTP_200_OK, safe=False)
        return response
    # need to close all db connections before forking, see
    # https://stackoverflow.com/questions/8242837/django-multiprocessing-and-database-connections/10684672#10684672

    p = Process(target=run_validation, kwargs={"validation_id": new_val_run.id})
    p.start()
    serializer = ValidationRunSerializer(new_val_run)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_validation_configuration(request, **kwargs):
    validation_run_id = kwargs['id']
    try:
        val_run = ValidationRun.objects.get(pk=validation_run_id)
        val_run_dict = {}

        val_run_dict['name_tag'] = val_run.name_tag

        if val_run.interval_from is not None:
            val_run_dict['interval_from'] = val_run.interval_from.date()
        else:
            val_run_dict['interval_from'] = None

        if val_run.interval_to is not None:
            val_run_dict['interval_to'] = val_run.interval_to.date()
        else:
            val_run_dict['interval_to'] = None

        if val_run.anomalies is not None:
            val_run_dict['anomalies_method'] = val_run.anomalies

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

        val_run_dict['scaling_method'] = val_run.scaling_method
        if val_run.scaling_method is not None or val_run.scaling_method != 'none':
            val_run_dict['scale_to'] = ValidationRun.SCALE_TO_REF
            if val_run.scaling_ref is not None:
                if val_run.scaling_ref.id != val_run.reference_configuration.id:
                    val_run_dict['scale_to'] = ValidationRun.SCALE_TO_DATA

        metrics = [{'id': 'tcol', 'value': val_run.tcol}]
        val_run_dict['metrics'] = metrics

        # Reference filters
        basic_filters = []
        for basic_filter in val_run.reference_configuration.filters.all():
            basic_filters.append(basic_filter.id)

        parametrised_filters = []
        for param_filter in ParametrisedFilter.objects.filter(dataset_config=val_run.reference_configuration):
            parametrised_filters.append({'id': param_filter.id, 'parameters': param_filter.parameters})

        val_run_dict['reference_config'] = {
            'dataset_id': val_run.reference_configuration.dataset.id,
            'version_id': val_run.reference_configuration.version.id,
            'variable_id': val_run.reference_configuration.variable.id,
            'basic_filters': basic_filters,
            'parametrised_filters': parametrised_filters
        }

        # dataset configs and filters
        datasets = []
        val_run_dict['dataset_configs'] = datasets
        for ds in val_run.dataset_configurations.all():
            if val_run.reference_configuration_id == ds.id:
                continue

            ds_dict = {'dataset_id': ds.dataset_id, 'version_id': ds.version_id, 'variable_id': ds.variable_id}
            filters_list = []
            ds_dict['basic_filters'] = filters_list
            for basic_filter in ds.filters.all():
                filters_list.append(basic_filter.id)

            parametrised_filters = []
            ds_dict['parametrised_filters'] = parametrised_filters
            for param_filter in ParametrisedFilter.objects.filter(dataset_config=ds):
                parametrised_filters.append({'id': param_filter.id, 'parameters': param_filter.parameters})

            datasets.append(ds_dict)

        return JsonResponse(val_run_dict,
                            status=status.HTTP_200_OK, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse(None, status=status.HTTP_404_NOT_FOUND, safe=False)


class DatasetConfigSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    dataset_id = serializers.IntegerField(required=True)
    version_id = serializers.IntegerField(required=True)
    variable_id = serializers.IntegerField(required=True)
    basic_filters = serializers.ListField(child=serializers.IntegerField(), required=True)


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

            new_val_run.save()

            # prepare DatasetConfiguration models
            reference_config = None
            dataset_config_models = []
            configs_to_save = [validated_data.get('reference_config')]
            configs_to_save.extend(validated_data.get('dataset_configs'))
            for config in configs_to_save:
                config_model = DatasetConfiguration.objects.create(validation=new_val_run,
                                                                   dataset_id=config.get('dataset_id'),
                                                                   version_id=config.get('version_id'),
                                                                   variable_id=config.get('variable_id'))
                config_model.save()
                filter_models = []
                for filter_id in config.get('basic_filters'):
                    filter_models.append(DataFilter.objects.get(id=filter_id))

                for filter_model in filter_models:
                    config_model.filters.add(filter_model)
                config_model.save()
                dataset_config_models.append(config_model)

            new_val_run.reference_configuration = dataset_config_models[0]
            scale_to = validated_data.get('scaling_method', None)
            if scale_to is not None:
                if scale_to == ValidationRun.SCALE_TO_DATA:
                    new_val_run.scaling_ref = dataset_config_models[1]
                else:
                    new_val_run.scaling_ref = dataset_config_models[0]

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
