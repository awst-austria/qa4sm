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
    """
    Here we can take all the filters or filters assigned to the particular dataset only.
    """
    dataset_id = request.query_params.get('dataset', None)
    # get filters assigned to a single dataset
    if dataset_id:
        data_filters = Dataset.objects.get(id=int(dataset_id)).filters
    # get all filters
    else:
        data_filters = DataFilter.objects.all()

    serializer = DataFilterSerializer(data_filters, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def data_filter_by_id(request, **kwargs):
#     dataset_filter = DataFilter.objects.get(pk=kwargs['id'])
#     serializer = DataFilterSerializer(dataset_filter)
#     return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def data_parameterised_filter(request):

    """
    Here we take the list of parameterized filters assigned to the particular configuration or
    list of all the parameterised filters applied to the existing validation.
    It's NOT a list od parameterised filters defined in the fixture! That one would be defined as:
    DataFilter.objects.filter(parameterised = True).
    """
    config_id = request.query_params.get('config', None)
    if config_id:
        param_filters = get_object_or_404(DatasetConfiguration, pk=config_id).parametrisedfilter_set.all()
    else:
        param_filters = ParametrisedFilter.objects.all()

    serializer = ParameterisedFilterSerializer(param_filters, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def data_parameterised_filter_by_id(request, **kwargs):
#     param_filters = ParametrisedFilter.objects.get(id=kwargs['id'])
#     serilizer = ParameterisedFilterSerializer(param_filters)
#     return JsonResponse(serilizer.data, status=status.HTTP_200_OK, safe=False)


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
