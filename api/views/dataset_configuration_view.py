from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import DatasetConfiguration


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_configuration(request):
    configs = DatasetConfiguration.objects.all()
    serializer = ConfigurationSerializer(configs, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_configuration_by_validation(request, **kwargs):
    configs = DatasetConfiguration.objects.filter(validation_id=kwargs['validation_id'])
    serializer = ConfigurationSerializer(configs, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class ConfigurationSerializer(ModelSerializer):
    class Meta:
        model = DatasetConfiguration
        fields = ['id',
                  'validation',
                  'dataset',
                  'version',
                  'variable',
                  'filters',
                  'parametrised_filters',
                  'parametrisedfilter_set',
                  'is_spatial_reference',
                  'is_temporal_reference',
                  'is_scaling_reference']
