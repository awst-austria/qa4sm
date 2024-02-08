import os

from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from validator.validation.globals import ISMN

from validator.models import DatasetVersion

GEOJSON_FILE_NAME = "ismn_sensors.json"


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_version_geojson_by_id(request, **kwargs):

    version = get_object_or_404(DatasetVersion, id=kwargs['version_id'])

    if version.versions.all().first().pretty_name != ISMN:
        return JsonResponse({'message': 'Not ISMN'}, status=status.HTTP_200_OK)

    if version.versions.count() != 1:
        return JsonResponse({'message': 'Dataset could not be determined'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)

    file_path = version.versions.all()[0].storage_path + "/" + version.short_name + "/" + GEOJSON_FILE_NAME

    if not os.path.exists(file_path):
        raise Http404("Geo-info file could not found")

    with open(file_path, "r") as geojson:
        return JsonResponse(geojson.read(), status=status.HTTP_200_OK, safe=False)
