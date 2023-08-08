from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from validator.models import DatasetVersion

GEOJSON_FILE_NAME = "geoinfo.json"


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_version_geojson_by_id(request, **kwargs):
    print(kwargs)
    version = get_object_or_404(DatasetVersion, id=kwargs['version_id'])
    if version.versions.count() != 1:
        return JsonResponse({'message': 'Dataset could not be determined'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)

    file_path = version.versions.all()[0].storage_path + "/" + version.short_name + "/" + GEOJSON_FILE_NAME

    with open(file_path, "r") as geojson:
        return JsonResponse(geojson.read(), status=status.HTTP_200_OK, safe=False)
