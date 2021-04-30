from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

from validator.models import ValidationRun
from validator.validation import generate_comparison, encode_plot


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comparison(request):
    # get validation comparison input
    validation_ids = request.query_params.getlist('ids', None)
    extent = request.query_params.get('extent', None)
    get_intersection = request.query_params.get('get_intersection', None)
    plot_types = request.query_params.getlist('plot_types', None)
    # generate the comparison
    validation_runs = []
    for val_id in validation_ids:
        validation = get_object_or_404(ValidationRun, id=val_id)
        validation_runs.append(validation)
    # resetting index added, otherwise there would be a row shift between the index column header and the header of the
    # rest of the columns when df rendered as html
    comparison = generate_comparison(
        validation_runs=validation_runs,
        extent=extent,
        get_intersection=get_intersection
    )
    # get comparison table (separate from plots)
    table = comparison.diff_table().reset_index()  # todo: how to include responses for downloads? Maybe further in the frontend?
    table = table.to_html(
        table_id=None,
        classes=['table', 'table-bordered', 'table-striped'],
        index=False
    )
    # save the comparison results in a dictionary
    comparison_data = {
        "table": table
    }
    for metric in comparison.common_metrics:
        comparison_data[metric] = []
        for plot_type in plot_types:
            base64_plot = encode_plot(
                comparison=comparison,
                plot_type=plot_type,
                metric=metric
            )
            comparison_data[metric].append(base64_plot)

    return HttpResponse(json.dumps(comparison_data))
