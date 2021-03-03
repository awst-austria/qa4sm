from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from validator.models import Dataset


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset(request):
    dataset_id = request.query_params.get('dataset_id', None)
    # datasets = []
    # # get single dataset
    if dataset_id:
        dataset = Dataset.objects.get(id=dataset_id)
        serializer = DatasetSerializer(dataset)
    # # get all datasets
    else:
        datasets = Dataset.objects.all()
        serializer = DatasetSerializer(datasets, many=True)

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
                  ]
