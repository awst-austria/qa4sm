from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import Dataset, DataFilter, DatasetConfiguration, ParametrisedFilter


@api_view(['GET'])
@permission_classes([AllowAny])
def data_filter(request):
    # All filters are taken
    data_filters = DataFilter.objects.all()
    serializer = DataFilterSerializer(data_filters, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


def data_filter_by_dataset(request,  **kwargs):
    # Here we can take all the filters or filters assigned to the particular dataset only.
    data_filters = get_object_or_404(Dataset, id=kwargs['id']).filters
    serializer = DataFilterSerializer(data_filters, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

@api_view(['GET'])
@permission_classes([AllowAny])
def data_parameterised_filter(request):

    """
    Here we take the list of all the parameterised filters applied to the existing validation.
    It's NOT a list od parameterised filters defined in the fixture! That one would be defined as:
    DataFilter.objects.filter(parameterised = True).
    """
    param_filters = ParametrisedFilter.objects.all()
    serializer = ParameterisedFilterSerializer(param_filters, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

#
# def data_parameterised_filter_by_config(request,  **kwargs):
#     # Here parameterized filters assigned to the particular configuration are taken
#     param_filters = get_object_or_404(DatasetConfiguration, pk=kwargs['id']).parametrisedfilter_set.all()
#     serializer = ParameterisedFilterSerializer(param_filters, many=True)
#     return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


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
                  'to_include',
                  'disable_filter'
                  ]


class ParameterisedFilterSerializer(ModelSerializer):
    class Meta:
        model = ParametrisedFilter
        fields = ['id',
                  'dataset_config_id',
                  'filter_id',
                  'parameters']
