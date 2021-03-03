from django.http import JsonResponse
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from api.dto import Dto
from validator.models import ValidationRun


@api_view(['POST'])
@permission_classes([AllowAny])
def start_validation(request):
    print(request.data)
    ser = NewValidationSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    return JsonResponse('{}', status=status.HTTP_200_OK, safe=False)


class DatasetConfigSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    dataset_id = serializers.IntegerField(required=True)
    version_id = serializers.IntegerField(required=True)
    variable_id = serializers.IntegerField(required=True)
    basic_filters = serializers.ListField(child=serializers.IntegerField(), required=True)


class DatasetConfigDto(Dto):
    def __init__(self, **kwargs):
        attributes = {'dataset_id', 'version_id', 'variable_id', 'basic_filters'}
        self.__create_attrs__(attributes)
        for key, value in kwargs.items():
            if key in attributes:
                setattr(self, key, value)


# Spatial subsetting DTO and serializer
class SpatialSubsetSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    min_lat = serializers.FloatField(required=False)
    min_lon = serializers.FloatField(required=False)
    max_lat = serializers.FloatField(required=False)
    max_lon = serializers.FloatField(required=False)


class SpatialSubsetDto(Dto):
    def __init__(self, **kwargs):
        attributes = {'min_lat', 'min_lon', 'max_lat', 'max_lon'}
        self.__create_attrs__(attributes)
        for key, value in kwargs.items():
            if key in attributes:
                setattr(self, key, value)


# Validation period DTO and serializer
class ValidationPeriodSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    interval_from = serializers.DateTimeField(required=False)
    interval_to = serializers.DateTimeField(required=False)


class ValidationPeriodDto(Dto):
    def __init__(self, **kwargs):
        attributes = {'interval_from', 'interval_to'}
        self.__create_attrs__(attributes)
        for key, value in kwargs.items():
            if key in attributes:
                setattr(self, key, value)


# Metrics DTO and serializer
class MetricsSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    id = serializers.CharField(required=True)
    value = serializers.BooleanField(required=True)


class MetricsDto(Dto):
    def __init__(self, **kwargs):
        attributes = {'id', 'value'}
        self.__create_attrs__(attributes)
        for key, value in kwargs.items():
            if key in attributes:
                setattr(self, key, value)


# Anomalies DTO and serializer
class AnomaliesSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    method = serializers.ChoiceField(choices=ValidationRun.ANOMALIES_METHODS, required=True)
    anomalies_from = serializers.DateTimeField(required=False)
    anomalies_to = serializers.DateTimeField(required=False)


class AnomaliesDto(Dto):
    def __init__(self, **kwargs):
        attributes = {'method', 'anomalies_from', 'anomalies_to'}
        self.__create_attrs__(attributes)
        for key, value in kwargs.items():
            if key in attributes:
                setattr(self, key, value)


# Scaling DTO and serializer
class ScalingSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    method = serializers.ChoiceField(choices=ValidationRun.SCALING_METHODS, required=True)
    scale_to = serializers.ChoiceField(choices=ValidationRun.SCALE_TO_OPTIONS, required=True)


class ScalingDto(Dto):
    def __init__(self, **kwargs):
        attributes = {'method', 'scale_to'}
        self.__create_attrs__(attributes)
        for key, value in kwargs.items():
            if key in attributes:
                setattr(self, key, value)


# New validation DTO that wraps the other DTOs
class NewValidationDto(Dto):
    """
    New validation run DTO with the necessary model fields
    """

    def __init__(self, **kwargs):
        attributes = {'dataset_configs', 'reference_config', 'spatial_subsetting', 'validation_period', 'metrics'}
        self.__create_attrs__(attributes)
        for key, value in kwargs.items():
            if key in attributes:
                setattr(self, key, value)


class NewValidationSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    dataset_configs = DatasetConfigSerializer(many=True, required=True)
    reference_config = DatasetConfigSerializer(required=True)
    spatial_subsetting = SpatialSubsetSerializer(required=True)
    validation_period = ValidationPeriodSerializer(required=True)
    metrics = MetricsSerializer(many=True, required=True)
    anomalies = AnomaliesSerializer(required=True)
    scaling = ScalingSerializer(required=True)
