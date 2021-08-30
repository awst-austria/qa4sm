from django.db.models import Q, ExpressionWrapper, F, BooleanField

from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import ModelSerializer

from api.views.auxiliary_functions import get_fields_as_list
from validator.forms import PublishingForm
from validator.models import ValidationRun
from validator.validation import get_inspection_table
from validator.validation.validation import copy_validationrun


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
                  'reference_configuration_id__dataset__pretty_name',
                  '-reference_configuration_id__dataset__pretty_name'
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
    order_list = ['name_tag',
                  '-name_tag',
                  'start_time',
                  '-start_time',
                  'progress',
                  '-progress',
                  'reference_configuration_id__dataset__pretty_name',
                  '-reference_configuration_id__dataset__pretty_name'
                  ]

    if order and order in order_list:
        val_runs = ValidationRun.objects.filter(user=current_user).order_by(order)
    elif not order:
        val_runs = ValidationRun.objects.filter(user=current_user)
    else:
        return JsonResponse({'message': 'Not appropriate order given'}, status=status.HTTP_400_BAD_REQUEST, safe=False)

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
    val_run = ValidationRun.objects.get(pk=kwargs['id'])
    if val_run is None:
        return JsonResponse(None, status=status.HTTP_404_NOT_FOUND, safe=False)

    serializer = ValidationRunSerializer(val_run)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def custom_tracked_validation_runs(request):
    current_user = request.user
    # taking only tracked validationruns, i.e. those with the same copied and original validationrun
    tracked_runs = current_user.copiedvalidations_set \
        .annotate(is_tracked=ExpressionWrapper(Q(copied_run=F('original_run')), output_field=BooleanField())) \
        .filter(is_tracked=True)

    # filtering copied runs by the tracked ones
    val_runs = current_user.copied_runs.filter(id__in=tracked_runs.values_list('original_run', flat=True))
    serializer = ValidationRunSerializer(val_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_summary_statistics(request):
    validation_id = request.query_params.get('id', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)
    # resetting index added, otherwise there would be a row shift between the index column header and the header of the
    # rest of the columns when df rendered as html
    inspection_table = get_inspection_table(validation).reset_index()

    return HttpResponse(inspection_table.to_html(table_id=None, classes=['table', 'table-bordered', 'table-striped'],
                                                 index=False))


@api_view(['GET'])
def get_publishing_form(request):
    validation_id = request.query_params.get('id', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)
    # validation = ValidationRun.objects.all()[0]
    publishing_form = PublishingForm(validation=validation)
    print(publishing_form.data)
    return JsonResponse(publishing_form.data, status=200)


@api_view(['GET'])
def copy_validation_results(request):
    validation_id = request.query_params.get('validation_id', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)
    current_user = request.user

    new_validation = copy_validationrun(validation, current_user)

    return JsonResponse(new_validation, status=200)


class ValidationRunSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(model)
