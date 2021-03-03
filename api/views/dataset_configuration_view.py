from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from validator.models import DatasetConfiguration


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_configuration(request):
    validation_id = request.query_params.get('validationrun', None)
    config_id = request.query_params.get('config_id', None)
    if validation_id:
        configs = DatasetConfiguration.objects.filter(validation_id=validation_id)
        serializer = ConfigurationSerializer(configs, many=True)
    elif config_id:
        config = DatasetConfiguration.objects.get(id = config_id)
        serializer = ConfigurationSerializer(config)
    else:
        configs = DatasetConfiguration.objects.all()
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
                  'parametrised_filters']
