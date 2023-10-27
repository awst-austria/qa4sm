from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import DatasetVersion, DataFilter, ParametrisedFilter

import logging

__logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def data_filter(request):
    # All filters are taken
    data_filters = DataFilter.objects.all()
    # data_filters.__log.debug(f'data_filters = {data_filters}')
    serializer = DataFilterSerializer(data_filters, many=True)
    # serializer.__log.debug(f'serializer = {serializer}')

    included_filters = check_included_filters(data_filters)
    if included_filters:
        # I don't overwrite the data_filter variable because here I'm returning a list not a query
        sorted_filters = sort_included_filters(list(data_filters), included_filters)
        serializer = DataFilterSerializer(sorted_filters, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)



@api_view(['GET'])
@permission_classes([AllowAny])
def data_filter_by_datasetversion(request, **kwargs):
    # Here we can take all the filters or filters assigned to the particular dataset only.
    data_filters = get_object_or_404(DatasetVersion, id=kwargs['version_id']).filters.all()
    serializer = DataFilterSerializer(data_filters, many=True)

    included_filters = check_included_filters(data_filters)
    if included_filters:
        # I don't overwrite the data_filter variable because here I'm returning a list not a query
        sorted_filters = sort_included_filters(list(data_filters), included_filters)
        serializer = DataFilterSerializer(sorted_filters, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def data_parameterised_filter(request):
    """
    Here we take the list of all the parameterised filters applied to the existing validation.
    It's NOT a list of parameterised filters defined in the fixture! That one would be defined as:
    DataFilter.objects.filter(parameterised = True).
    """
    param_filters = ParametrisedFilter.objects.all()
    serializer = ParameterisedFilterSerializer(param_filters, many=True)
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
                  'to_include',
                  'to_exclude',
                  'default_set_active',
                  'readonly'
                  ]


class ParameterisedFilterSerializer(ModelSerializer):
    class Meta:
        model = ParametrisedFilter
        fields = ['id',
                  'dataset_config_id',
                  'filter_id',
                  'parameters']


def get_ind_of_model_item_in_list(item_list, key, value):
    for item in item_list:
        if getattr(item, key) == value:
            return item_list.index(item)
    return


def check_included_filters(filters):
    filters_with_included = filters.exclude(to_include=None)
    if len(filters_with_included) == 0:
        return
    else:
        # if there are, take their ids
        included_filters_list = [{
            'filter': filter_item.id,
            'filters_included': filter_item.to_include.split(',')
        } for filter_item in filters_with_included]
        return included_filters_list


def sort_included_filters(filters, included_filters):
    for filter_item in included_filters:
        filter_item_ind_on_list = get_ind_of_model_item_in_list(filters, 'id', filter_item['filter'])
        for ind, included_filter_id in enumerate(filter_item['filters_included']):
            ind_of_included_filter = get_ind_of_model_item_in_list(filters, 'id', int(included_filter_id))
            filters.insert(filter_item_ind_on_list + ind + 1, filters.pop(ind_of_included_filter))
    return filters
