from django.http import JsonResponse

from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from validator.models import ValidationRun
from validator.validation import generate_comparison, get_comparison_plot

import matplotlib as pl
pl.use('Agg')
import matplotlib.pyplot as plt

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comparison(request):
    validation_ids = request.query_params.get('ids', None)
    extent = request.query_params.get('extent', None)
    get_intersection = request.query_params.get('get_intersection', None)

    validation_runs = []
    for id in validation_ids:
        validation = get_object_or_404(ValidationRun, id=validation_id)
        validation_runs.append(validation)
    # resetting index added, otherwise there would be a row shift between the index column header and the header of the
    # rest of the columns when df rendered as html
    comparison = generate_comparison(
        validation_runs=validation_runs,
        extent=extent,
        get_intersection=get_intersection
    )

    return HttpResponse(comparison)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comparison_table(request):
    comparison = request.query_params.get('comparison', None)

    diff_table = get_comparison_plot(
        comparison=comparison,
        plot_type="table"
    )

    return HttpResponse(diff_table)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_comparison_table(request):
    comparison = request.query_params.get('comparison', None)

    diff_table = get_comparison_plot(
        comparison=comparison,
        plot_type="table"
    )

    return HttpResponse(diff_table)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getimage(request):
    comparison = request.query_params.get('comparison', None)
    plot_type = request.query_params.get('plot_type', None)
    metric = request.query_params.get('metric', None)

    get_comparison_plot(
        comparison=comparison,
        plot_type=plot_type,
        metric=metric
    )

    response = HttpResponse(content_type="image/jpeg")
    plt.savefig(response, format="png")

    return response