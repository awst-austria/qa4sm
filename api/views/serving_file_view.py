import base64
import os
from collections import OrderedDict

from django.conf import settings
from django.core.files import File
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from validator.models import ValidationRun, DatasetConfiguration, Dataset

import mimetypes
from wsgiref.util import FileWrapper
from validator.validation import get_inspection_table, get_inspection_table_spatial, get_dataset_combis_and_metrics_from_files, get_dataset_combis_and_metrics_from_files_spatial
from validator.validation.globals import ISMN, METADATA_PLOT_NAMES, ISMN_LIST_FILE_NAME, TC_METRICS


@api_view(['GET'])
@permission_classes([AllowAny])
def get_results(request):
    validation_id = request.query_params.get('validationId', None)
    file_type = request.query_params.get('fileType', None)
    validation = get_object_or_404(ValidationRun, pk=validation_id)

    try:
        file_path = validation.output_dir_url.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
    except AttributeError:
        return HttpResponse('Given validation has no output directory assigned', status=404)

    if file_type == 'netCDF':
        filename = file_path + validation.output_file_name
    elif file_type == 'graphics':
        filename = file_path + 'graphs.zip'
    else:
        return HttpResponse('No file type given', status=404)

    try:
        file_wrapper = FileWrapper(open(filename, 'rb'))
    except FileNotFoundError as e:
        return HttpResponse(e, status=404)

    file_mimetype = mimetypes.guess_type(filename)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csv_with_statistics(request):
    """Download .csv of the statistics"""
    validation_id = request.query_params.get('validationId', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)

    try:
        inspection_table = get_inspection_table(validation)
    except FileNotFoundError as e:
        return HttpResponse('File not found', 404)

    if isinstance(inspection_table, str):
        return HttpResponse('error file size', 404)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Stats_summary.csv'

    inspection_table.reset_index().to_csv(
        path_or_buf=response,
        sep=',',
        float_format='%.2f',
        index=False,
        decimal="."
    )

    return response

def build_status_boxplot_dicts(files, file_path, barplot_prefix):
    """
    Builds boxplot_dicts for status metric, linking each barplot to its overview file.
    Handles pairs (barplot_status_*) and triples (barplot_tc_status_*).
    """
    boxplot_dicts = []
    ind = 0

    # collect pairs: bulk_barplot_status_0-ISMN_and_1-C3S_combined.png
    pair_files = sorted([f for f in files 
                         if f.startswith(barplot_prefix + 'status_')
                         and 'tc_status' not in f])
    
    for f in pair_files:
        # extract pair name: '0-ISMN_and_1-C3S_combined'
        pair_key = f.replace(barplot_prefix + 'status_', '').replace('.png', '')
        pretty_name = pair_key.replace('_', ' ')
        
        # find matching overview: bulk_overview_0-ISMN_and_1-C3S_combined*status.png
        overview = [file_path + o for o in files 
                    if o.startswith(f'bulk_overview_{pair_key}') 
                    and o.endswith('_status.png')]
        
        boxplot_dicts.append({
            'ind': ind,
            'name': pretty_name,
            'file': file_path + f,
            'overview_files': overview
        })
        ind += 1

    # collect triples: bulk_barplot_tc_status_0-ISMN_and_1-C3S_combined_and_2-ERA5.png
    triple_files = sorted([f for f in files 
                           if f.startswith(barplot_prefix + 'tc_status_')])
    
    for f in triple_files:
        triple_key = f.replace(barplot_prefix + 'tc_status_', '').replace('.png', '')
        pretty_name = triple_key.replace('_', ' ')
        
        overview = [file_path + o for o in files 
                    if o.startswith(f'bulk_overview_{triple_key}') 
                    and o.endswith('_status.png')]
        
        boxplot_dicts.append({
            'ind': ind,
            'name': pretty_name,
            'file': file_path + f,
            'overview_files': overview
        })
        ind += 1

    return boxplot_dicts if boxplot_dicts else [{'ind': 0, 'name': 'Unclassified', 'file': '', 'overview_files': []}]



@api_view(['GET'])
@permission_classes([AllowAny])
def get_metric_names_and_associated_files(request):
    validation_id = request.query_params.get('validationId', None)
    validation = get_object_or_404(ValidationRun, pk=validation_id)
    ref_dataset_name = DatasetConfiguration.objects.get(
        id=validation.spatial_reference_configuration_id).dataset.pretty_name

    dataset_configs = DatasetConfiguration.objects.filter(
        validation_id=validation.id
    ).order_by('-is_spatial_reference', '_order')

    dataset_names = [
        f"{i}-{config.dataset.short_name}"
        for i, config in enumerate(dataset_configs)
    ]

    bulk_prefix = ''
    seasonal_prefix = ''
    seasonal_files_path = ''

    try:
        file_path = validation.output_dir_url.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
    except AttributeError:
        return JsonResponse({'message': 'Given validation has no output directory assigned'}, status=404)

    try:
        path_content = os.listdir(file_path)

        if validation.intra_annual_metrics or validation.stability_metrics:
            seasonal_prefix = 'comparison_boxplot'

        if f'{seasonal_prefix}s' in path_content:
            seasonal_files_path = file_path + f'{seasonal_prefix}s/'

        if "bulk" in path_content:
            file_path += 'bulk/'
            bulk_prefix = 'bulk_'

        boxplot_prefix = bulk_prefix + 'boxplot_'
        barplot_prefix = bulk_prefix + 'barplot_'
        overview_prefix = bulk_prefix + 'overview_'
    except FileNotFoundError:
        return JsonResponse({'message': 'Output directory does not contain any files.'}, status=404)

    seasonal_files = []
    if seasonal_files_path:
        seasonal_files = os.listdir(seasonal_files_path)
        if len(seasonal_files) == 0:
            return JsonResponse({'message': 'Comparison files have not been created'}, status=404)

    try:
        files = os.listdir(file_path)
        if len(files) == 0 or not any(file.endswith('.png') for file in files):
            return JsonResponse({'message': 'There are no result files in the given directory'}, status=404)
    except FileNotFoundError as e:
        return JsonResponse({'message': str(e)}, status=404)

    pairs, triples, metrics, ref0_config, zarr_metrics, zarr_var_list = get_dataset_combis_and_metrics_from_files(
        validation, dataset_names)
    combis = OrderedDict(sorted({**pairs, **triples}.items()))
    metrics = OrderedDict(sorted([(v, k) for k, v in metrics.items()]))
    response = []

    tc_metric_keys = list(TC_METRICS.keys())  # ['snr', 'err_std', 'beta']
    overview_independent_metrics = ['n_obs']

    for metric_ind, key in enumerate(metrics):
        seasonal_metric_file = ''
        seasonal_file_name = seasonal_prefix + '_' + metrics[key] + '.png'

        if metrics[key] == 'status':
            boxplot_type = 'dataset_combination'
            boxplot_dicts = build_status_boxplot_dicts(files, file_path, barplot_prefix)
            overview_files = []
            datasets = []

        else:
            boxplot_type = 'classification'

            # check if TC metric: snr_3-ERA5, err_std_1-C3S_combined, beta_2-ERA5
            is_tc_metric = any(metrics[key].startswith(tc + '_') for tc in tc_metric_keys)

            if is_tc_metric:
                # file uses '_for_': snr_3-ERA5 → bulk_boxplot_snr_for_3-ERA5.png
                tc_key = next(tc for tc in tc_metric_keys if metrics[key].startswith(tc + '_'))
                ds_part = metrics[key][len(tc_key) + 1:]  # '3-ERA5'
                file_suffix = f'{tc_key}_for_{ds_part}'   # 'snr_for_3-ERA5'
                boxplot_file_name = boxplot_prefix + file_suffix + '.png'
            else:
                file_suffix = metrics[key]
                boxplot_file_name = boxplot_prefix + metrics[key] + '.png'

            boxplot_file = file_path + boxplot_file_name if boxplot_file_name in files else ''
            boxplot_dicts = [{'ind': 0, 'name': 'Unclassified', 'file': boxplot_file, 'overview_files': []}]

            if ref_dataset_name == ISMN:
                metadata_plots = [
                    {'file_name': boxplot_prefix + file_suffix + '_' + metadata_name + '.png'}
                    for metadata_name in METADATA_PLOT_NAMES.values()
                ]
                plot_ind = 1
                for meta_ind, file_dict in enumerate(metadata_plots):
                    if file_dict['file_name'] in files:
                        boxplot_dicts.append({
                            'ind': plot_ind,
                            'name': list(METADATA_PLOT_NAMES.keys())[meta_ind],
                            'file': file_path + file_dict['file_name'],
                            'overview_files': []
                        })
                        plot_ind += 1

            if is_tc_metric:
                # overview files end with _{tc_key}_for_{ds_part}.png
                # e.g. bulk_overview_0-ISMN_and_1-C3S_and_2-ERA5_snr_for_3-ERA5.png
                overview_suffix = f'_{file_suffix}.png'
                tc_overview_files = [
                    f for f in files
                    if f.startswith(overview_prefix)
                    and f.endswith(overview_suffix)
                ]
                overview_files = [file_path + f for f in tc_overview_files]
                datasets = [
                    f.replace(overview_prefix, '')
                     .replace(overview_suffix, '')
                     .replace('_', ' ')
                    for f in tc_overview_files
                ]

            elif metrics[key] not in overview_independent_metrics:
                overview_plots = [
                    {'file_name': overview_prefix + name_key + '_' + metrics[key] + '.png',
                     'datasets': name_key}
                    for name_key in combis
                ]
                overview_files = [file_path + file_dict['file_name'] for file_dict in overview_plots
                                  if file_dict['file_name'] in files]
                datasets = [' '.join(file_dict['datasets'].split('_')) for file_dict in overview_plots
                           if file_dict['file_name'] in files]

            else:
                overview_plots = [{'file_name': overview_prefix + metrics[key] + '.png', 'datasets': ''}]
                overview_files = [file_path + file_dict['file_name'] for file_dict in overview_plots
                                  if file_dict['file_name'] in files]
                datasets = [' '.join(file_dict['datasets'].split('_')) for file_dict in overview_plots
                           if file_dict['file_name'] in files]

        if len(seasonal_files) and seasonal_file_name in seasonal_files:
            seasonal_metric_file = [seasonal_files_path + seasonal_file_name]

        metric_dict = {
            'ind': metric_ind,
            'metric_query_name': metrics[key],
            'metric_pretty_name': key,
            'boxplot_type': boxplot_type,
            'boxplot_dicts': boxplot_dicts,
            'overview_files': overview_files,
            'metadata_files': [],
            'comparison_boxplot': seasonal_metric_file,
            'zarr_metrics': zarr_metrics,
            'zarr_var_list': zarr_var_list,
            'datasets': datasets,
        }
        response.append(metric_dict)

    return JsonResponse(response, status=200, safe=False)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_graphic_files(request):
    # Here we take a list of parameters 'file' and return a list of plots encoded to base64
    files = request.query_params.getlist('file', None)
    if not files:
        return JsonResponse({'message': 'No file names given'}, status=404, safe=False)
    plots = []
    for file in files:
        if '/static/' in file:
            file = file.replace('/static/', os.path.join(settings.BASE_DIR, 'validator/static/'))
        open_file = open(file, 'rb')
        image = File(open_file)
        name = base64.b64encode(image.read())
        open_file.close()
        plots.append({'plot': name.decode('utf-8')})
    return JsonResponse(plots, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_graphic_file(request):
    # Here we take only one file and return one plot;
    # Sometimes it's just easier to read a single file, and this function is created not to refer to index 0 every time
    file = request.query_params.get('file', None)
    if not file:
        return JsonResponse({'message': 'No file name given'}, status=404, safe=False)
    if '/static/' in file:
        file = file.replace('/static/', os.path.join(settings.BASE_DIR, 'validator/static/'))
    open_file = open(file, 'rb')
    image = File(open_file)
    name = base64.b64encode(image.read())
    open_file.close()

    return JsonResponse({'plot': name.decode('utf-8')}, safe=True)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_summary_statistics(request):
    """Show statistics table on results page"""
    validation_id = request.query_params.get('id', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)
    # resetting index added, otherwise there would be a row shift between the index column header and the header of the
    # rest of the columns when df rendered as html

    try:
        inspection_table = get_inspection_table(validation)
    except FileNotFoundError as e:
        return HttpResponse('File not found', 404)

    if isinstance(inspection_table, str):
        return HttpResponse('error file size')

    return HttpResponse(
        inspection_table.reset_index().to_html(
            table_id=None,
            classes=['table', 'table-bordered', 'table-striped'],
            index=False
        ))

@api_view(['GET'])
@permission_classes([AllowAny])
def get_summary_statistics_spatial(request):
    validation_id = request.query_params.get('id', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)

    try:
        inspection_table = get_inspection_table_spatial(validation)
    except FileNotFoundError as e:
        return HttpResponse('File not found', 404)

    if inspection_table is None:
        return HttpResponse('File not found', 404)

    if isinstance(inspection_table, str):
        return HttpResponse('error file size')

    return HttpResponse(
        inspection_table.reset_index().to_html(
            table_id=None,
            classes=['table', 'table-bordered', 'table-striped'],
            index=False
        ))


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_manual(request):
    # Read from settings (string path). Support relative paths by resolving against BASE_DIR.
    manual_path = getattr(settings, "USER_MANUAL_PATH", "")
    if manual_path and not os.path.isabs(manual_path):
        manual_path = os.path.abspath(os.path.join(settings.BASE_DIR, manual_path))

    if not manual_path or not os.path.isfile(manual_path):
        return HttpResponse('User manual not found', status=404)

    try:
        file_wrapper = FileWrapper(open(manual_path, 'rb'))
    except FileNotFoundError:
        return HttpResponse('User manual not found', status=404)

    file_mimetype, _ = mimetypes.guess_type(manual_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype or 'application/pdf')
    # inline in the browser; use 'attachment;' to force download
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(manual_path)}"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ismn_list_file(request):
    ismn_ds = get_object_or_404(Dataset, short_name='ISMN')
    file_path = f'{ismn_ds.storage_path}/{ISMN_LIST_FILE_NAME}'

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="data.csv"'
            return response
    else:
        return HttpResponse("File not found", status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_results_spatial(request):
    validation_id = request.query_params.get('validationId', None)
    file_type = request.query_params.get('fileType', None)
    validation = get_object_or_404(ValidationRun, pk=validation_id)

    run_dir = os.path.join(settings.MEDIA_ROOT, str(validation.id)) + '/'

    if file_type == 'netCDF':
        filename = run_dir + validation.output_file_spatial_name
        download_name = f"{validation.id}_spatial.nc"
    elif file_type == 'graphics':
        filename = run_dir + 'spatial_graphs.zip'
        download_name = f"{validation.id}_spatial_graphs.zip"
    elif file_type == 'statistics':
        filename = run_dir + 'spatial_statistics.zip'
        download_name = f"{validation.id}_spatial_statistics.zip"
    else:
        return HttpResponse('No file type given', status=404)

    try:
        file_wrapper = FileWrapper(open(filename, 'rb'))
    except FileNotFoundError as e:
        return HttpResponse(e, status=404)

    file_mimetype = mimetypes.guess_type(filename)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['Content-Disposition'] = f'attachment; filename="{download_name}"'
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_metric_names_and_associated_files_spatial(request):
    validation_id = request.query_params.get('validationId', None)
    validation = get_object_or_404(ValidationRun, pk=validation_id)

    try:
        plot_dir = os.path.join(settings.MEDIA_ROOT, str(validation.id), 'bulk', 'spatial') + '/'
        files = os.listdir(plot_dir)
    except FileNotFoundError as e:
        return JsonResponse({'message': str(e)}, status=404)

    if not any(f.endswith('.png') for f in files):
        return JsonResponse({'message': 'No spatial plot files found'}, status=404)

    # take metrics pretty names
    _, _, metrics, _ = get_dataset_combis_and_metrics_from_files_spatial(validation)

    if not metrics:
        return JsonResponse({'message': 'No metrics found'}, status=404)
    
    priority = ['n_obs', 'status']
    prioritized = {k: metrics[k] for k in priority if k in metrics}
    rest = {k: v for k, v in sorted(metrics.items()) if k not in priority}
    metrics = {**prioritized, **rest}

    # all overview files in folder
    all_overview_files = sorted([
        f for f in files
        if f.startswith('bulk_overview_') and f.endswith('_n_gpi_was_used.png')
    ])

    independent_metrics = ['n_obs', 'status']
    barplot_prefix = 'bulk_barplot_'
    boxplot_prefix = 'bulk_boxplot_spatial_'
    tsplot_prefix  = 'bulk_tsplot_'

    response = []

    for ind, (metric_query, metric_pretty) in enumerate(metrics.items()):

        # --- overview files ---
        metric_overview_files = []
        metric_datasets = []

        for ov in all_overview_files:
            combi_key = ov \
                .removeprefix('bulk_overview_') \
                .removesuffix('_n_gpi_was_used.png')

            is_triple = combi_key.count('_and_') == 2
            is_pair   = combi_key.count('_and_') == 1

            if metric_query in independent_metrics:
                include = True
            elif '_for_' in metric_query:
                ds_with_id = metric_query.split('_for_')[1]   
                ds_name = '-'.join(ds_with_id.split('-')[1:])  
                include = is_triple and ds_name in combi_key
            else:
                include = is_pair

            if include:
                metric_overview_files.append(plot_dir + ov)
                metric_datasets.append(combi_key.replace('_', ' '))

        # --- boxplot / barplot ---
        if metric_query == 'status':
            boxplot_dicts = build_status_boxplot_dicts(files, plot_dir, barplot_prefix)
        else:
            bf = f'{boxplot_prefix}{metric_query}.png'
            boxplot_dicts = [{'ind': 0, 'name': 'Boxplot',
                               'file': plot_dir + bf if bf in files else ''}]

        # --- tsplot ---
        tf = f'{tsplot_prefix}{metric_query}.png'
        tsplot = [plot_dir + tf] if tf in files else []

        response.append({
            'ind': ind,
            'metric_query_name': metric_query,
            'metric_pretty_name': metric_pretty,  
            'boxplot_dicts': boxplot_dicts,
            'overview_files': metric_overview_files,
            'metadata_files': [],
            'comparison_boxplot': [],
            'datasets': metric_datasets,
            'tsplot_file': tsplot,
        })

    return JsonResponse(response, status=200, safe=False)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_metric_names_and_associated_files_spatial_old(request):
    validation_id = request.query_params.get('validationId', None)
    validation = get_object_or_404(ValidationRun, pk=validation_id)

    try:
        file_path = os.path.join(settings.MEDIA_ROOT, str(validation.id)) + '/'
        plot_dir = os.path.join(file_path, 'bulk', 'spatial') + '/'

        try:
            files = os.listdir(plot_dir)
            if not any(f.endswith('.png') for f in files):
                return JsonResponse({'message': 'No spatial plot files found'}, status=404)
        except FileNotFoundError as e:
            return JsonResponse({'message': str(e)}, status=404)

        # parsing function for spatial validation
        pairs, triples, metrics, ref0_config = get_dataset_combis_and_metrics_from_files_spatial(validation)
        combis = OrderedDict(sorted({**pairs, **triples}.items()))
        metrics = OrderedDict(sorted([(val, key) for key, val in metrics.items()]))

        response = []
        boxplot_prefix = 'bulk_boxplot_spatial_'
        tsplot_prefix = 'bulk_tsplot_'
        barplot_prefix = 'bulk_barplot_'
        independent_metrics = ['n_obs', 'status']

        for metric_ind, key in enumerate(metrics):

            boxplot_file = ''
            tsplot_file = ''
            metric_query = metrics[key]  # 'R', 'snr_for_1-C3S_combined', 'status'...

            # relevant combinations for overview
            if metric_query in independent_metrics:
                # n_obs, status → all combinations. Need to discuss.
                relevant_combis = combis

            elif '_for_' in metric_query:
                # TC metrics → only triples with the relevant dataset
                # 'snr_for_1-C3S_combined' → ds_met = '1-C3S_combined'
                ds_met = metric_query.split('_for_')[1]
                relevant_combis = OrderedDict(
                    (k, v) for k, v in combis.items()
                    if k.count('_and_') == 2  # triple
                    and ds_met in k            # dataset participates
                )

            else:
                # ordinary metrics → only pairs with the relevant dataset
                relevant_combis = OrderedDict(
                    (k, v) for k, v in combis.items()
                    if k.count('_and_') == 1  
                )

            # combining overview files and datasets for the metric
            metric_overview_files = []
            metric_datasets = []
            for combi, pretty_name in relevant_combis.items():
                overview_file = plot_dir + f'bulk_overview_{combi}_n_gpi_was_used.png'
                if os.path.exists(overview_file):
                    metric_overview_files.append(overview_file)
                    metric_datasets.append(pretty_name)

            # boxplot files
            if metric_query == 'status':
                barplot_files = [f for f in files if f.startswith(barplot_prefix + 'status')]
                boxplot_file_name = barplot_files[0] if barplot_files else ''
            else:
                boxplot_file_name = boxplot_prefix + metric_query + '.png'

            # tsplot files
            tsplot_file_name = tsplot_prefix + metric_query + '.png'

            if boxplot_file_name and boxplot_file_name in files:
                boxplot_file = plot_dir + boxplot_file_name

            if tsplot_file_name in files:
                tsplot_file = plot_dir + tsplot_file_name

            metric_dict = {
                'ind': metric_ind,
                'metric_query_name': metric_query,
                'metric_pretty_name': key,
                'boxplot_dicts': [{'ind': 0, 'name': 'Boxplot', 'file': boxplot_file}],
                'overview_files': metric_overview_files,
                'metadata_files': [],
                'comparison_boxplot': [],
                'datasets': metric_datasets,
                'tsplot_file': [tsplot_file] if tsplot_file else [],
            }
            response.append(metric_dict)

        return JsonResponse(response, status=200, safe=False)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'message': str(e)}, status=500)