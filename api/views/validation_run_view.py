from django.db.models import Q, ExpressionWrapper, F, BooleanField

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import ModelSerializer

from api.views.auxiliary_functions import get_fields_as_list
from validator.models import ValidationRun, CopiedValidations



@api_view(['GET'])
@permission_classes([AllowAny])
def published_results(request):
    limit = request.query_params.get('limit', None)
    offset = request.query_params.get('offset', None)
    order = request.query_params.get('order', None)
    order_list = ['name_tag',
                  '-name_tag',
                  'start_time',
                  '-start_time',
                  'progress',
                  '-progress',
                  'spatial_reference_configuration_id__dataset__pretty_name',
                  '-spatial_reference_configuration_id__dataset__pretty_name'
                  ]

    if order and order in order_list:
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
    order = request.query_params.get('order', None)

    filterVar = request.query_params.get('filterVar', None)

    order_list = ['name_tag',
                  '-name_tag',
                  'start_time',
                  '-start_time',
                  'progress',
                  '-progress',
                  'spatial_reference_configuration_id__dataset__pretty_name',
                  '-spatial_reference_configuration_id__dataset__pretty_name'
                  ]

    if order and order in order_list:
        val_runs = ValidationRun.objects.filter(user=current_user).order_by(order)
    elif not order:
        val_runs = ValidationRun.objects.filter(user=current_user)
    else:
        return JsonResponse({'message': 'Not appropriate order given'}, status=status.HTTP_400_BAD_REQUEST, safe=False)

    # Apply the filterVar if provided and not empty
    if filterVar:
        val_runs = val_runs.filter(name_tag__icontains=filterVar)


    if limit and offset:
        limit = int(limit)
        offset = int(offset)
        serializer = ValidationRunSerializer(val_runs[offset:(offset + limit)], many=True)
    else:
        serializer = ValidationRunSerializer(val_runs, many=True)

    response = {'validations': serializer.data, 'length': len(val_runs)}

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


class ValidationRunSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(model)


class CopiedValidationRunSerializer(ModelSerializer):
    class Meta:
        model = CopiedValidations
        fields = get_fields_as_list(model)
