from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import Dataset


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset(request):
    datasets = Dataset.objects.all()
    serializer = DatasetSerializer(datasets, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_by_id(request, **kwargs):
    ds = get_object_or_404(Dataset, pk=kwargs['id'])
    serializer = DatasetSerializer(ds)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class DatasetSerializer(ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id',
                  'short_name',
                  'pretty_name',
                  'help_text',
                  'storage_path',
                  'detailed_description',
                  'source_reference',
                  'citation',
                  'is_only_reference',
                  'versions',
                  'variables',
                  'filters',
                  'not_as_reference'
                  ]
