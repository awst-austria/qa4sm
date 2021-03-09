from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from api.views.validation_run_view import ResultsSerializer
from validator.models import ValidationRun, DatasetConfiguration, DataFilter


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_validation(request):
    print(request.data)
    ser = NewValidationSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    new_val_run = ser.save(user=request.user)
    new_val_run.user = request.user
    new_val_run.save()

    serializer = ResultsSerializer(new_val_run)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


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


class NewValidationSerializer(serializers.Serializer):
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
