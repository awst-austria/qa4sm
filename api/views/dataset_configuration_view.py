from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer, RelatedField, PrimaryKeyRelatedField
from api.views.auxiliary_functions import get_fields_as_list

from validator.models import DatasetConfiguration


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_configuration(request):
    validation_id = request.query_params.get('validationrun', None)
    if validation_id:
        configs = DatasetConfiguration.objects.filter(validation_id=validation_id)
    else:
        configs = DatasetConfiguration.objects.all()

    print(configs)

    serializer = ConfigurationSerializer(configs, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class ConfigurationSerializer(ModelSerializer):
    class Meta:
        model = DatasetConfiguration
        fields = ['validation',
                  'dataset',
                  'version',
                  'variable',
                  'filters',
                  'parametrised_filters']
