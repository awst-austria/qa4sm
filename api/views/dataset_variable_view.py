from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import Dataset, DataVariable


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_variable(request):
    dataset_id = request.query_params.get('dataset', None)
    variable_id = request.query_params.get('variable_id', None)

    if variable_id:
        variable = DataVariable.objects.get(id=variable_id)
        serializer = DatasetVariableSerializer(variable)
    else:
        if dataset_id:
            variables = Dataset.objects.get(id=dataset_id).variables
        else:
            variables = DataVariable.objects.all()

        serializer = DatasetVariableSerializer(variables, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_variable_by_id(request, **kwargs):
    ds = DataVariable.objects.get(pk=kwargs['id'])
    serializer = DatasetVariableSerializer(ds)
    print(serializer.data)
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
                  ]
