import json
import os
from functools import lru_cache

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import DataVariable, DatasetVersion

VERSIONS_FIXTURE_PATH = os.path.join(settings.BASE_DIR, 'validator', 'fixtures', 'versions.json')


@lru_cache(maxsize=1)
def _version_variable_order():
    # variable order per version is only recorded as list position in versions.json,
    # there is no order column on the DatasetVersion<->DataVariable relation
    with open(VERSIONS_FIXTURE_PATH) as f:
        entries = json.load(f)
    return {entry['pk']: entry['fields']['variables']
            for entry in entries if entry['model'] == 'validator.datasetversion'}


def _sort_variables_by_fixture_order(version_id, variables):
    order = _version_variable_order().get(version_id)
    if not order:
        return variables
    order_index = {variable_id: index for index, variable_id in enumerate(order)}
    return sorted(variables, key=lambda variable: order_index.get(variable.id, len(order)))


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
def dataset_variable_by_version(request, **kwargs):
    version = get_object_or_404(DatasetVersion, id=kwargs['version_id'])
    variables = _sort_variables_by_fixture_order(version.id, list(version.variables.all()))
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
                  'unit',
                  'display_name'
                  ]
