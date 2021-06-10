from django.db.models import Q, ExpressionWrapper, F, BooleanField

from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated

from api.views.auxiliary_functions import get_fields_as_list
from validator.models import ValidationRun
from validator.validation import get_inspection_table



@api_view(['GET'])
@permission_classes([AllowAny])
def published_results(request):

    limit = request.query_params.get('limit', None)
    offset = request.query_params.get('offset', None)
    order = request.query_params.get('order',None)

    if order:
        val_runs = ValidationRun.objects.exclude(doi='').order_by(order)
    else:
        val_runs = ValidationRun.objects.exclude(doi='')

    if limit and offset:
        limit = int(limit)
        offset = int(offset)
        serializer = ValidationRunSerializer(val_runs[offset:(offset+limit)], many=True)
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

    if order:
        val_runs = ValidationRun.objects.filter(user=current_user).order_by(order)
    else:
        val_runs = ValidationRun.objects.filter(user=current_user)

    if limit and offset:
        limit = int(limit)
        offset = int(offset)
        serializer = ValidationRunSerializer(val_runs[offset:(offset+limit)], many=True)
    else:
        serializer = ValidationRunSerializer(val_runs, many=True)

    response = {'validations': serializer.data, 'length': len(val_runs)}

    return JsonResponse(response, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validation_runs(request, **kwargs):
    val_runs = ValidationRun.objects.all()
    serializer = ValidationRunSerializer(val_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validation_run_by_id(request, **kwargs):
    val_run = ValidationRun.objects.get(pk=kwargs['id'])
    if val_run is None:
        return JsonResponse(None, status=status.HTTP_404_NOT_FOUND, safe=False)

    serializer = ValidationRunSerializer(val_run)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def custom_tracked_validation_runs(request):
    current_user = request.user
    # taking only tracked validationruns, i.e. those with the same copied and original validationrun
    tracked_runs = current_user.copiedvalidations_set\
        .annotate(is_tracked=ExpressionWrapper(Q(copied_run=F('original_run')), output_field=BooleanField()))\
        .filter(is_tracked=True)

    # filtering copied runs by the tracked ones
    val_runs = current_user.copied_runs.filter(id__in=tracked_runs.values_list('original_run', flat=True))
    serializer = ValidationRunSerializer(val_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_summary_statistics(request):
    validation_id = request.query_params.get('id', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)
    # resetting index added, otherwise there would be a row shift between the index column header and the header of the
    # rest of the columns when df rendered as html
    inspection_table = get_inspection_table(validation).reset_index()

    response = HttpResponse(inspection_table.to_html(table_id=None, classes=['table', 'table-bordered', 'table-striped'],
                                                 index=False))

    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_validations_for_comparison(request):
    ref_dataset = request.query_params.get('ref_dataset', 'ISMN')
    ref_version = request.query_params.get('ref_version', 'ISMN_V20191211')
    # by default, take 2 datasets at maximum
    max_non_reference_datasets = int(request.query_params.get('max_datasets', 1))
    max_datasets = max_non_reference_datasets + 1  # add the reference
    # filter the validation runs based on the reference dataset/version
    ref_filtered = ValidationRun.objects.filter(
        reference_configuration__dataset__short_name=ref_dataset,
        reference_configuration__version__short_name=ref_version,
    ).exclude(
        output_file='')
    # filter based on the number of non-reference datasets
    eligible4comparison = []
    for val in ref_filtered:
        if val is None:
            continue
        if val.dataset_configurations.count() == max_datasets:
            eligible4comparison.append(val)

    if not eligible4comparison:
        return JsonResponse(None, status=status.HTTP_200_OK, safe=False)

    serializer = ValidationRunSerializer(eligible4comparison, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class ValidationRunSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(model)
