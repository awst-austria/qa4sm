import base64
import os
from collections import OrderedDict

from django.core.files import File
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

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

    pairs, triples, metrics, ref0_config = get_dataset_combis_and_metrics_from_files(validation)
    combis = OrderedDict(sorted({**pairs, **triples}.items()))
    metrics = OrderedDict(sorted([(v, k) for k, v in metrics.items()]))
    response = []

    for ind, key in enumerate(metrics):
        boxplot_file = ''
        boxplot_file_name = 'boxplot_' + metrics[key] + '.png'

        # 'n_obs' doesn't refer to datasets so I create a list with independent metrics, if there are other similar
        # metrics it's just enough to add them here:
        independent_metrics = ['n_obs']

        if metrics[key] not in independent_metrics:
            overview_plots = [{'file_name': 'overview_' + name_key + '_' + metrics[key] + '.png',
                               'datasets': name_key} for name_key in combis]
        else:
            overview_plots = [{'file_name': 'overview_' + metrics[key] + '.png', 'datasets': ''}]

        if boxplot_file_name in files:
            boxplot_file = file_path + boxplot_file_name
        overview_files = [file_path + file_dict['file_name'] for file_dict in overview_plots if file_dict['file_name'] in files]
        datasets = [file_dict['datasets'] for file_dict in overview_plots if file_dict['file_name'] in files]
        metric_dict = {'ind': ind,
                       'metric_query_name': metrics[key],
                       'metric_pretty_name': key,
                       'boxplot_file': boxplot_file,
                       'overview_files': overview_files,
                       'datasets': datasets}
        response.append(metric_dict)
    #
    return JsonResponse(response, status=200, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_graphic_file(request):
    files = request.query_params.getlist('file', None)
    plots = []
    for file in files:
        if '/static/' in file:
            file = file.replace('/static/', os.path.join(settings.BASE_DIR, 'validator/static/'))
        open_file = open(file, 'rb')
        image = File(open_file)
        name = base64.b64encode(image.read())
        open_file.close()
        plots.append({'plot': str(name).lstrip("b'").rstrip("'")})

    return JsonResponse(plots, safe=False)

