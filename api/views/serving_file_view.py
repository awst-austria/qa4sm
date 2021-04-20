import base64
import os
from collections import OrderedDict

from django.core.files import File
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from validator.models import ValidationRun
from django.conf import settings

import mimetypes
from wsgiref.util import FileWrapper

from validator.validation import get_inspection_table, get_dataset_combis_and_metrics_from_files


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_results(request):
    validation_id = request.query_params.get('validationId', None)
    file_type = request.query_params.get('fileType', None)
    validation = get_object_or_404(ValidationRun, pk=validation_id)
    file_path = validation.output_dir_url.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
    if file_type == 'netCDF':
        filename = file_path + validation.output_file_name
    else:
        filename = file_path + 'graphs.zip'
    file_wrapper = FileWrapper(open(filename, 'rb'))
    file_mimetype = mimetypes.guess_type(filename)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_csv_with_statistics(request):

    validation_id = request.query_params.get('validationId', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)
    inspection_table = get_inspection_table(validation).reset_index()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Stats_summary.csv'

    inspection_table.to_csv(path_or_buf=response, sep=',', float_format='%.2f', index=False, decimal=".")
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_metric_names_and_associated_files(request):
    validation_id = request.query_params.get('validationId', None)
    validation = get_object_or_404(ValidationRun, pk=validation_id)
    file_path = validation.output_dir_url.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
    files = os.listdir(file_path)

    _, _, metrics, _ = get_dataset_combis_and_metrics_from_files(validation)
    metrics = OrderedDict(sorted([(v, k) for k, v in metrics.items()]))

    response = []
    for key in metrics:
        boxplot_file = ''
        overview_files = []
        for file in files:
            if metrics[key] in file and 'boxplot' in file:
                boxplot_file = file_path + file
            if metrics[key] in file and 'overview' in file:
                overview_files.append(file_path + file)

        metric_dict = {'metric_query_name': metrics[key],
                       'metric_pretty_name': key,
                       'boxplot_file': boxplot_file,
                       'overview_files': overview_files}
        response.append(metric_dict)

    return JsonResponse(response, status=200, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_result_graphic_files(request):
    file = request.query_params.get('file', None)

    open_file = open(file, 'rb')
    image = File(open_file)
    name = base64.b64encode(image.read())
    open_file.close()

    # file_wrapper = FileWrapper(open(file, 'rb'))
    # file_mimetype = mimetypes.guess_type(file)

    response = HttpResponse(name)

    return response

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_result_graphic_files(request):
#     files = request.query_params.getlist('files', None)
#     print('files', type(files), files)
#     data = []
#     for file in files:
#         open_file = open(file, 'rb')
#         image = File(open_file)
#         name = str(base64.b64encode(image.read()))
#         name_dict = {'coded_name': name.lstrip("b'")}
#         data.append(name_dict)
#         open_file.close()
#
#     # file_wrapper = FileWrapper(open(file, 'rb'))
#     # file_mimetype = mimetypes.guess_type(file)
#
#     response = JsonResponse(data, safe=False)
#
#     return response


