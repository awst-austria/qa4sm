from multiprocessing.context import Process

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connections
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer

from api.views.auxiliary_functions import get_fields_as_list
from api.views.validation_run_view import ValidationRunSerializer
from validator.models import ValidationRun, DatasetConfiguration, DataFilter
from validator.validation import run_validation


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_validation(request):
    print(request.data)
    ser = ValidationConfigurationSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    new_val_run = ser.save(user=request.user)
    new_val_run.user = request.user
    new_val_run.save()

    # need to close all db connections before forking, see
    # https://stackoverflow.com/questions/8242837/django-multiprocessing-and-database-connections/10684672#10684672
    connections.close_all()

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
        val_run_dict['id'] = val_run.id
        val_run_dict['scaling_ref'] = val_run.scaling_ref
        val_run_dict['scaling_method'] = val_run.scaling_method
        val_run_dict['interval_from'] = val_run.interval_from
        val_run_dict['interval_to'] = val_run.interval_to
        val_run_dict['anomalies'] = val_run.anomalies
        val_run_dict['min_lat'] = val_run.min_lat
        val_run_dict['min_lon'] = val_run.min_lon
        val_run_dict['max_lat'] = val_run.max_lat
        val_run_dict['max_lon'] = val_run.max_lon
        val_run_dict['anomalies_from'] = val_run.anomalies_from
        val_run_dict['anomalies_to'] = val_run.anomalies_to
        val_run_dict['tcol'] = val_run.tcol
        val_run_dict['ref_dataset_config'] = val_run.reference_configuration_id
        validation_run_serializer = ValidationRunSerializer(val_run)

        datasets = []
        val_run_dict['dataset_configs'] = datasets
        for ds in val_run.dataset_configurations.all():
            ds_dict = {}
            ds_dict['id'] = ds.id
            ds_dict['dataset'] = ds.dataset_id
            ds_dict['version'] = ds.version_id
            ds_dict['variable'] = ds.variable_id
            filters_list = []
            ds_dict['filters'] = filters_list
            for filter in ds.filters.all():
                filters_list.append(filter.id)

            param_filters_list = []
            ds_dict['param_filters'] = param_filters_list
            for filter in ds.parametrised_filters.all():
                param_filters_list.append({'id': filter.filter.id, 'parameters': filter.parameters})
            datasets.append(ds_dict)
        # configs = ValidationConfigurationModelSerializer(validation_run.dataset_configurations.all(), many=True)
        return JsonResponse({'val': val_run_dict, 'val2': datasets},
                            status=status.HTTP_404_NOT_FOUND, safe=False)
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


# Spatial subsetting DTO and serializer
class SpatialSubsetSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    min_lat = serializers.FloatField(required=False, default=34.0)
    min_lon = serializers.FloatField(required=False, default=-11.2)
    max_lat = serializers.FloatField(required=False, default=71.6)
    max_lon = serializers.FloatField(required=False, default=48.3)


# Validation period DTO and serializer
class ValidationPeriodSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    interval_from = serializers.DateTimeField(required=False)
    interval_to = serializers.DateTimeField(required=False)


# Metrics DTO and serializer
class MetricsSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    id = serializers.CharField(required=True)
    value = serializers.BooleanField(required=True)


# Anomalies DTO and serializer
class AnomaliesSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    method = serializers.ChoiceField(choices=ValidationRun.ANOMALIES_METHODS, required=True)
    anomalies_from = serializers.DateTimeField(required=False)
    anomalies_to = serializers.DateTimeField(required=False)


# Scaling DTO and serializer
class ScalingSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    method = serializers.ChoiceField(choices=ValidationRun.SCALING_METHODS, required=True)
    scale_to = serializers.ChoiceField(choices=ValidationRun.SCALE_TO_OPTIONS, required=True)


class ValidationConfigurationSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):

        with transaction.atomic():
            # prepare ValidationRun model
            new_val_run = ValidationRun(start_time=timezone.now())
            new_val_run.interval_from = validated_data.get('validation_period').get('interval_from', None)
            new_val_run.interval_to = validated_data.get('validation_period').get('interval_to', None)
            new_val_run.anomalies = validated_data.get('anomalies').get('method')
            new_val_run.anomalies_from = validated_data.get('anomalies').get('anomalies_from', None)
            new_val_run.anomalies_to = validated_data.get('anomalies').get('anomalies_to', None)
            new_val_run.min_lat = validated_data.get('spatial_subsetting').get('min_lat', None)
            new_val_run.min_lon = validated_data.get('spatial_subsetting').get('min_lon', None)
            new_val_run.max_lat = validated_data.get('spatial_subsetting').get('max_lat', None)
            new_val_run.max_lon = validated_data.get('spatial_subsetting').get('max_lon', None)
            new_val_run.scaling_method = validated_data.get('scaling').get('method', None)

            for metric in validated_data.get('metrics'):
                if metric.get('id') == 'tcol':
                    new_val_run.tcol = metric.get('value')

            new_val_run.save()

            # prepare DatasetConfiguration models
            reference_config = None
            dataset_config_models = []
            configs_to_save = [validated_data.get('reference_config')]
            print('Reference config:')
            print(configs_to_save)
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
            new_val_run.save()

        return new_val_run

    dataset_configs = DatasetConfigSerializer(many=True, required=True)
    reference_config = DatasetConfigSerializer(required=True)
    spatial_subsetting = SpatialSubsetSerializer(required=True)
    validation_period = ValidationPeriodSerializer(required=True)
    metrics = MetricsSerializer(many=True, required=True)
    anomalies = AnomaliesSerializer(required=True)
    scaling = ScalingSerializer(required=True)


class ValidationConfigurationModelSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(model)
