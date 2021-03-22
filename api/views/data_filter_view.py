from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import Dataset, DataFilter


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def data_filter(request):
    dataset_id = request.query_params.get('dataset', None)
    # # get single dataset
    if dataset_id:
        data_filters = Dataset.objects.get(id=dataset_id).filters
    # get all datasets
    else:
        data_filters = DataFilter.objects.all()

    serializer = DataFilterSerializer(data_filters, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def data_filter_by_id(request, **kwargs):
    # filter_id = request.query_params.get(pk=kwargs['id'])
    dataset_filter = DataFilter.objects.get(pk=kwargs['id'])
    serializer = DataFilterSerializer(dataset_filter)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class DataFilterSerializer(ModelSerializer):
    class Meta:
        model = DataFilter
        fields = ['id',
                  'name',
                  'description',
                  'help_text',
                  'parameterised',
                  'dialog_name',
                  'default_parameter',
                  ]
