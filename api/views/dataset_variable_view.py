from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import ModelSerializer

from validator.models import Dataset, DataVariable


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_variable(request):
    variables = DataVariable.objects.all().order_by('-id')
    serializer = DatasetVariableSerializer(variables, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_variable_by_id(request, **kwargs):
    variable = get_object_or_404(DataVariable, id=kwargs['variable_id'])
    serializer = DatasetVariableSerializer(variable)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_variable_by_dataset(request, **kwargs):
    variables = get_object_or_404(Dataset, id=kwargs['dataset_id']).variables.order_by('id')
    serializer = DatasetVariableSerializer(variables, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class DatasetVariableSerializer(ModelSerializer):
    class Meta:
        model = DataVariable
        fields = ['id',
                  'short_name',
                  'pretty_name',
                  'help_text',
                  'min_value',
                  'max_value',
                  'unit'
                  ]
