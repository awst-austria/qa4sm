import os
import netCDF4
from django.db.models import Q, ExpressionWrapper, F, BooleanField

from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated

from api.views.auxiliary_functions import get_fields_as_list
from validator.forms import PublishingForm
from validator.models import ValidationRun, CopiedValidations
from validator.validation import get_inspection_table
from datetime import datetime
from validator.validation.util import mkdir_if_not_exists
from validator.validation.globals import OUTPUT_FOLDER
from shutil import copy2
from dateutil.tz import tzlocal
from django.conf import settings
from django.urls.base import reverse
from api.frontend_urls import get_angular_url


def _copy_validationrun(run_to_copy, new_user):
    # checking if the new validation belongs to the same user:
    if run_to_copy.user == new_user:
        run_id = run_to_copy.id
        # belongs_to_user = True
    else:
        # copying validation
        valrun_user = CopiedValidations(used_by_user=new_user, original_run=run_to_copy)
        valrun_user.save()

        # old info which is needed then
        old_scaling_ref_id = run_to_copy.scaling_ref_id
        old_val_id = str(run_to_copy.id)

        dataset_conf = run_to_copy.dataset_configurations.all()

        run_to_copy.user = new_user
        run_to_copy.id = None
        run_to_copy.start_time = datetime.now(tzlocal())
        run_to_copy.end_time = datetime.now(tzlocal())
        run_to_copy.save()
        run_id = run_to_copy.id

        # adding the copied validation to the copied validation list
        valrun_user.copied_run = run_to_copy
        valrun_user.save()

        # new configuration
        for conf in dataset_conf:
            old_id = conf.id
            old_filters = conf.filters.all()
            old_param_filters = conf.parametrisedfilter_set.all()

            # setting new scaling reference id
            if old_id == old_scaling_ref_id:
                run_to_copy.scaling_ref_id = conf.id

            new_conf = conf
            new_conf.pk = None
            new_conf.validation = run_to_copy
            new_conf.save()

            # setting filters
            new_conf.filters.set(old_filters)
            if len(old_param_filters) != 0:
                for param_filter in old_param_filters:
                    param_filter.id = None
                    param_filter.dataset_config = new_conf
                    param_filter.save()

        # the reference configuration is always the last one:
        try:
            run_to_copy.reference_configuration_id = conf.id
            run_to_copy.save()
        except:
            pass

        # copying files
        # new directory -> creating if doesn't exist
        new_dir = os.path.join(OUTPUT_FOLDER, str(run_id))
        mkdir_if_not_exists(new_dir)
        # old directory and all files there
        old_dir = os.path.join(OUTPUT_FOLDER, old_val_id)
        old_files = os.listdir(old_dir)

        if len(old_files) != 0:
            for file_name in old_files:
                new_file = new_dir + '/' + file_name
                old_file = old_dir + '/' + file_name
                copy2(old_file, new_file)
                if '.nc' in new_file:
                    run_to_copy.output_file = str(run_id) + '/' + file_name
                    run_to_copy.save()
                    file = netCDF4.Dataset(new_file, mode='a', format="NETCDF4")

                    # with netCDF4.Dataset(new_file, mode='a', format="NETCDF4") as file:
                    new_url = settings.SITE_URL + get_angular_url('result', run_id)
                    file.setncattr('url', new_url)
                    file.setncattr('date_copied', run_to_copy.start_time.strftime('%Y-%m-%d %H:%M'))
                    file.close()

    response = {
        'run_id': run_id,
    }
    return response

@api_view(['GET'])
@permission_classes([AllowAny])
def published_results(request):
    limit = request.query_params.get('limit', None)
    offset = request.query_params.get('offset', None)
    order = request.query_params.get('order', None)

    if order:
        val_runs = ValidationRun.objects.exclude(doi='').order_by(order)
    else:
        val_runs = ValidationRun.objects.exclude(doi='')

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
@permission_classes([AllowAny])
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
        serializer = ValidationRunSerializer(val_runs[offset:(offset + limit)], many=True)
    else:
        serializer = ValidationRunSerializer(val_runs, many=True)

    response = {'validations': serializer.data, 'length': len(val_runs)}

    return JsonResponse(response, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def validation_runs(request, **kwargs):
    val_runs = ValidationRun.objects.all()
    serializer = ValidationRunSerializer(val_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


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

    new_validation = _copy_validationrun(validation, current_user)

    return JsonResponse(new_validation, status=200)


class ValidationRunSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(model)
