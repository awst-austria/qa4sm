import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import Dataset, User, UserDatasetFile


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset(request):
    user_data = json.loads(request.query_params.get('userData', 'false'))
    exclude_no_files = json.loads(request.query_params.get('excludeNoFiles', 'true'))
    user = request.user
    datasets = Dataset.objects.filter(user=None)
    if user_data and user.is_authenticated:
        user_datasets = Dataset.objects.filter(user=user)
        datasets = datasets.union(user_datasets.exclude(storage_path='')) if exclude_no_files else datasets.union(
            user_datasets)

        # check if there is data that has been shared with the logged-in user
        if user.belongs_to_data_management_groups:
            shared_datasets = Dataset.objects.filter(user_groups__in=user.data_management_groups()).exclude(
                storage_path='') if exclude_no_files else Dataset.objects.filter(user_groups__in=user.data_management_groups())
            datasets = datasets.union(shared_datasets)

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
                  'is_spatial_reference',
                  'versions',
                  'variables',
                  #   'filters',
                  'not_as_reference',
                  'user',
                  'is_shared'
                  ]
