from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import DatasetVersion, Dataset


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_version(request):
    versions = DatasetVersion.objects.all()
    serializer = DatasetVersionSerializer(versions, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_version_by_id(request, **kwargs):
    version = get_object_or_404(DatasetVersion, id=kwargs['version_id'])
    serializer = DatasetVersionSerializer(version)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_version_by_dataset(request, **kwargs):
    versions = get_object_or_404(Dataset, id=kwargs['dataset_id']).versions
    serializer = DatasetVersionSerializer(versions, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

class DatasetVersionSerializer(ModelSerializer):
    class Meta:
        model = DatasetVersion
        fields = ['id',
                  'short_name',
                  'pretty_name',
                  'help_text',
                  'filters', # new
                  'time_range_start',
                  'time_range_end',
                  'geographical_range'
                  ]
