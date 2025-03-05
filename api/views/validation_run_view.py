from dateutil import parser
from datetime import datetime
from django.db.models import Q, ExpressionWrapper, F, BooleanField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework.authentication import TokenAuthentication

from api.views.auxiliary_functions import get_fields_as_list
from validator.models import ValidationRun, CopiedValidations

ORDER_LIST = {
    'name:asc': 'name_tag',
    'name:desc': '-name_tag',
    'start_time:asc': 'start_time',
    'start_time:desc': '-start_time',
    'progress:asc': 'progress',
    'progress:desc': '-progress',
    'spatial_reference_dataset:asc': 'spatial_reference_configuration_id__dataset__pretty_name',
    'spatial_reference_dataset:desc': '-spatial_reference_configuration_id__dataset__pretty_name'
}

# ORDER_LIST = ['name_tag',
#               '-name_tag',
#               'start_time',
#               '-start_time',
#               'progress',
#               '-progress',
#               'spatial_reference_configuration_id__dataset__pretty_name',
#               '-spatial_reference_configuration_id__dataset__pretty_name'
#               ]

@api_view(['GET'])
@permission_classes([AllowAny])
def published_results(request):
    limit = request.query_params.get('limit', None)
    offset = request.query_params.get('offset', None)
    order_name = request.query_params.get('order', None)
    order = ORDER_LIST.get(order_name, None)

    if order and order in ORDER_LIST:
        val_runs = ValidationRun.objects.exclude(doi='').order_by(order)
    elif not order:
        val_runs = ValidationRun.objects.exclude(doi='')
    else:
        return JsonResponse({'message': 'Not appropriate order given'}, status=status.HTTP_400_BAD_REQUEST, safe=False)

    # both limit and offset are send as string, so the simple if limit and offset condition can be used,
    # if they were sent as numbers there would be a problem because they both can be 0
    if limit and offset:
        limit = int(limit)
        offset = int(offset)
        serializer = ValidationRunSerializer(val_runs[offset:(offset + limit)], many=True)
    else:
        serializer = ValidationRunSerializer(val_runs, many=True)

    response = {'validations': serializer.data,
                'length': len(val_runs)}

    return JsonResponse(response, status=status.HTTP_200_OK, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_results(request):
    current_user = request.user
    limit = request.query_params.get('limit', None)
    offset = request.query_params.get('offset', None)
    order_name = request.query_params.get('order', None)
    order = ORDER_LIST.get(order_name, None)


    user_validations = ValidationRun.objects.filter(user=current_user)

    for parameter in request.query_params:
        if parameter.startswith('filter'):
            filter_query = parameter.split(':')[1]
            values = request.query_params.get(parameter, None).split(',')
            print(filter_query, values)



    if order and order in ORDER_LIST :
        user_validations = user_validations.order_by(order)
    elif order not in ORDER_LIST:
        return JsonResponse({'message': 'Not appropriate order given'}, status=status.HTTP_400_BAD_REQUEST, safe=False)

    if limit and offset:
        limit = int(limit)
        offset = int(offset)
        serializer = ValidationRunSerializer(user_validations[offset:(offset + limit)], many=True)
    else:
        serializer = ValidationRunSerializer(user_validations, many=True)

    response = {'validations': serializer.data, 'length': len(user_validations)}

    return JsonResponse(response, status=status.HTTP_200_OK, safe=False)



@api_view(['GET'])
@permission_classes([AllowAny])
def validation_run_by_id(request, **kwargs):
    val_run = get_object_or_404(ValidationRun, pk=kwargs['id'])
    if val_run is None:
        return JsonResponse(None, status=status.HTTP_404_NOT_FOUND, safe=False)

    serializer = ValidationRunSerializer(val_run)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def custom_tracked_validation_runs(request):
    current_user = request.user
    # taking only tracked validationruns, i.e. those with the same copied and original validationrun
    tracked_runs = current_user.copiedvalidations_set \
        .annotate(is_tracked=ExpressionWrapper(Q(copied_run=F('original_run')), output_field=BooleanField())) \
        .filter(is_tracked=True)
    # filtering runs by the tracked ones
    val_runs = ValidationRun.objects.filter(id__in=tracked_runs.values_list('original_run', flat=True))
    serializer = ValidationRunSerializer(val_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_validations_for_comparison(request):
    current_user = request.user
    ref_dataset = request.query_params.get('ref_dataset', 'ISMN')
    ref_version = request.query_params.get('ref_version', 'ISMN_V20191211')
    # by default, take 2 datasets at maximum
    max_non_reference_datasets = int(request.query_params.get('max_datasets', 1))
    max_datasets = max_non_reference_datasets + 1  # add the reference
    # filter the validation runs based on the reference dataset/version
    ref_filtered = ValidationRun.objects.filter(
        spatial_reference_configuration__dataset__short_name=ref_dataset,
        spatial_reference_configuration__version__short_name=ref_version,
    ).exclude(
        output_file='')

    ref_filter_owned = ref_filtered.filter(user=current_user)
    ref_filter_published_not_owned = ref_filtered.exclude(doi='').exclude(user=current_user)

    ref_for_comparison = ref_filter_owned.union(ref_filter_published_not_owned)

    # filter based on the number of non-reference datasets
    eligible4comparison = []
    for val in ref_for_comparison:
        if val is None:
            continue
        if val.dataset_configurations.count() == max_datasets:
            eligible4comparison.append(val)

    if not eligible4comparison:
        return JsonResponse(None, status=status.HTTP_200_OK, safe=False)

    serializer = ValidationRunSerializer(eligible4comparison, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_copied_validations(request, **kwargs):
    copied_run = get_object_or_404(CopiedValidations, copied_run_id=kwargs['id'])
    serializer = CopiedValidationRunSerializer(copied_run)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def is_validation_finished(request, **kwargs):

    val_run = get_object_or_404(ValidationRun, pk=kwargs['id'])
    if not val_run:
        return JsonResponse(status=status.HTTP_404_NOT_FOUND)

    ifFinished = (val_run.progress == 100 and val_run.end_time is not None)
    return JsonResponse({'validation_complete': ifFinished}, status=status.HTTP_200_OK)

def filter_by_validation_statuses(validation_statuses):
    #Horrible code to apply set of job status filters.
    # this function will be replaced with a simple filtering when we create a proper field
    status_filters = Q()
    for status in validation_statuses:
        if status == 'Scheduled':
            status_filters |= Q(progress=0, end_time__isnull=True)
        elif status == 'Done':
            status_filters |= Q(progress=100, end_time__isnull=False)
        elif status == 'Cancelled':
            status_filters |= Q(progress__lt=0)
        elif status == 'ERROR':
            status_filters |= Q(end_time__isnull=False, total_points=0)
            #status_filters |= Q(total_points=0)
        elif status == 'Running':
            status_filters |= Q(progress__gte=0, progress__lt=100, end_time__isnull=True, total_points__gt=0)
        else:
            print('Status didnt match')
    return status_filters

class ValidationRunSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(model)


class CopiedValidationRunSerializer(ModelSerializer):
    class Meta:
        model = CopiedValidations
        fields = get_fields_as_list(model)
