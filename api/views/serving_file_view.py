from collections import OrderedDict

from django.http import FileResponse, HttpResponse
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
def get_result_graphic_files(request):
    validation_id = request.query_params.get('validationId', None)
    validation = get_object_or_404(ValidationRun, pk=validation_id)

    pairs, triples, metrics, ref0_config = get_dataset_combis_and_metrics_from_files(validation)
    combis = OrderedDict(sorted({**pairs, **triples}.items()))
    metrics = OrderedDict(sorted([(v, k) for k, v in metrics.items()]))

