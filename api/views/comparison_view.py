from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from qa4sm_reader.comparing import ComparisonError, SpatialExtentError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

from validator.models import ValidationRun
from validator.validation import comparison_table, encoded_comparisonPlots, generate_comparison, get_extent_image


def get_validations(ids):
    validation_runs = []
    for val_id in ids:
        validation = get_object_or_404(ValidationRun, id=val_id)
        validation_runs.append(validation)

    return validation_runs


def get_table(request):
    """Get the comparison table as a html table"""
    validation_ids = request.query_params.getlist('ids', None)
    metric_list = request.query_params.getlist('metric_list', None)
    extent = request.query_params.get('extent', None)
    get_intersection = request.query_params.get('get_intersection', 'false')
    validation_runs = get_validations(validation_ids)
    try:
        table = comparison_table(
            validation_runs=validation_runs,
            metric_list=metric_list,
            extent=extent,
            get_intersection=json.loads(get_intersection)
        ).reset_index()
        return table

    except (SpatialExtentError, ComparisonError) as e:
        return str(e)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comparison_table(request):
    """Get the comparison table as a html table"""
    table = get_table(request)
    try:
        response = HttpResponse(
            table.to_html(
                table_id=None,
                classes=['table', 'table-bordered', 'table-striped', 'comparison'],
                index=False)
        )
    except AttributeError as e:
        response = HttpResponse(str(e))
    except Exception as e:
        response = HttpResponse(str(e))
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_comparison_table(request):
    """Download the table as a .csv file"""
    table = get_table(request)
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Comparison_summary.csv'
        table.to_csv(path_or_buf=response, sep=',', float_format='%.2f', index=False, decimal=".")

    except AttributeError as e:
        response = HttpResponse(str(e))
    except Exception as e:
        response = HttpResponse(str(e))

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comparison_metrics(request):
    """Get the metrics that are common to all validations"""
    validation_ids = request.query_params.getlist('ids', None)
    get_intersection = request.query_params.get('get_intersection', 'false')
    validation_runs = get_validations(validation_ids)
    try:
        comp = generate_comparison(
            validation_runs,
            get_intersection=json.loads(get_intersection)
        )
        response = []
        for short_name, pretty_name in comp.common_metrics.items():
            metric_dict = {'metric_query_name': short_name,
                           'metric_pretty_name': pretty_name}
            response.append(metric_dict)

    except (SpatialExtentError, ComparisonError) as e:
        response = [{'message': str(e)}]
    except Exception as e:
        response = [{'message': str(e)}]
    return JsonResponse(response, status=200, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comparison_plots_for_metric(request):
    """Get all the comparison plots as a base64 encoding"""
    validation_ids = request.query_params.getlist('ids', None)
    plot_types = request.query_params.getlist('plot_types', None)
    metric = request.query_params.get('metric', None)
    extent = request.query_params.get('extent', None)
    get_intersection = request.query_params.get('get_intersection', 'false')
    validation_runs = get_validations(validation_ids)

    encoded_plots = []
    for plot_type in plot_types:
        try:
            base64_plot = encoded_comparisonPlots(
                validation_runs=validation_runs,
                plot_type=plot_type,
                metric=metric,
                extent=extent,
                get_intersection=json.loads(get_intersection)
            )

            encoded_plots.append({'plot': base64_plot})

        except (SpatialExtentError, ComparisonError):
            continue
        except Exception as e:
            continue

    if not encoded_plots:
        return JsonResponse(
            [{'message': str("No plot could be produced from the selected comparison")}],
            status=200, safe=False
        )

    return JsonResponse(encoded_plots, status=200, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_spatial_extent(request):
    """Get an image with the spatial extent of the comparison"""
    get_intersection = request.query_params.get('get_intersection', 'false')
    validation_ids = request.query_params.getlist('ids', None)
    validation_runs = get_validations(validation_ids)
    try:
        encoded_image = get_extent_image(
            validation_runs=validation_runs,
            get_intersection=json.loads(get_intersection)
        )
    except SpatialExtentError as e:
        return JsonResponse([{'message': str(e)}], status=200, safe=False)
    except Exception as e:
        return JsonResponse([{'message': str(e)}], status=200, safe=False)
    if not encoded_image == "error encountered":
        return JsonResponse(encoded_image, status=200, safe=False)
