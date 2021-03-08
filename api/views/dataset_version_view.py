from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from validator.models import DatasetVersion, Dataset


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_version(request):
    dataset_id = request.query_params.get('dataset', None)
    version_id = request.query_params.get('version_id', None)
    # # get single dataset
    if version_id:
        version = DatasetVersion.objects.get(id=version_id)
        serializer = DatasetVersionSerializer(version)
    else:
        if dataset_id:
            versions = Dataset.objects.get(id=dataset_id).versions
        # get all datasets
        else:
            versions = DatasetVersion.objects.all()

        serializer = DatasetVersionSerializer(versions, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_version_by_id(request, **kwargs):
    ds = DatasetVersion.objects.get(pk=kwargs['id'])
    serializer = DatasetVersionSerializer(ds)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class DatasetVersionSerializer(ModelSerializer):
    class Meta:
        model = DatasetVersion
        fields = ['id',
                  'short_name',
                  'pretty_name',
                  'help_text',
                  'time_range_start',
                  'time_range_end',
                  ]
