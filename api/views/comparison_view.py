from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

from validator.models import ValidationRun
from validator.validation import comparison_table, encoded_comparisonPlots, generate_comparison


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comparisonTable(request):
    """Get the comparison table as an html table"""
    validation_ids = request.query_params.getlist('ids', None)
    metric_list = request.query_params.get('metric_list', None)
    extent = request.query_params.get('extent', None)
    get_intersection = request.query_params.get('get_intersection', None)
    validation_runs = []
    for val_id in validation_ids:
        validation = get_object_or_404(ValidationRun, id=val_id)
        validation_runs.append(validation)
        # resetting index added, otherwise there would be a row shift between the index column header and the header of the
    # rest of the columns when df rendered as html
    table = comparison_table(
            validation_runs=validation_runs,
            metric_list=metric_list,
            extent=extent,
            get_intersection=get_intersection
        ).reset_index()
    table = table.to_html(
        table_id=None,
        classes=['table', 'table-bordered', 'table-striped'],
        index=False
    )

    return HttpResponse(table)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_comparison_table(request):
    """Dowanload the table as a .csv file"""
    validation_ids = request.query_params.getlist('ids', None)
    metric_list = request.query_params.get('metric_list', None)
    extent = request.query_params.get('extent', None)
    get_intersection = request.query_params.get('get_intersection', None)
    validation_runs = []
    for val_id in validation_ids:
        validation = get_object_or_404(ValidationRun, id=val_id)
        validation_runs.append(validation)
        # resetting index added, otherwise there would be a row shift between the index column header and the header of the
    # rest of the columns when df rendered as html
    table = comparison_table(
            validation_runs=validation_runs,
            metric_list=metric_list,
            extent=extent,
            get_intersection=get_intersection
        ).reset_index()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Comparison_summary.csv'

    table.to_csv(path_or_buf=response, sep=',', float_format='%.2f', index=False, decimal=".")
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comparison_metrics(request):
    """Get the metrics that are common to all validations"""
    validation_ids = request.query_params.getlist('ids', None)
    validation_runs = []
    for val_id in validation_ids:
        validation = get_object_or_404(ValidationRun, id=val_id)
        validation_runs.append(validation)

    comp = generate_comparison(validation_runs)

    return HttpResponse(comp.common_metrics)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comparisonPlots4Metric(request):
    """Get all the comparison plots as a base64 encoding"""
    validation_ids = request.query_params.getlist('ids', None)
    plot_types = request.query_params.getlist('plot_types', None)
    metric = request.query_params.get('metric', None)
    extent = request.query_params.get('extent', None)
    get_intersection = request.query_params.get('get_intersection', None)
    validation_runs = []
    for val_id in validation_ids:
        validation = get_object_or_404(ValidationRun, id=val_id)
        validation_runs.append(validation)

    encoded_plots = []
    for plot_type in plot_types:
        base64_plot = encoded_comparisonPlots(
            validation_runs=validation_runs,
            plot_type=plot_type,
            metric=metric,
            extent=extent,
            get_intersection=get_intersection
        )
        encoded_plots.append(base64_plot)

    return HttpResponse(encoded_plots)
