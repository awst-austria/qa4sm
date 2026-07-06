import os
import re

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# <report_date>_<creation_date>_<indicator>.pdf, e.g. 20260131_202606290613_G.pdf
REPORT_FILENAME_REGEX = re.compile(
    r'^(?P<report_date>\d{8})_(?P<creation_date>\d{12})_(?P<indicator>[GYR])\.pdf$'
)
# series = directory name, e.g. SMOS_L2_v700; no slashes/dots -> no path traversal
SERIES_NAME_REGEX = re.compile(r'^[A-Za-z0-9_.-]+$')


def _autoreports_dir():
    """Resolve AUTOREPORTS_DIR; relative paths are resolved against BASE_DIR (local dev)."""
    reports_dir = getattr(settings, 'AUTOREPORTS_DIR', '')
    if reports_dir and not os.path.isabs(reports_dir):
        reports_dir = os.path.abspath(os.path.join(settings.BASE_DIR, reports_dir))
    return reports_dir


def _get_series_dir_or_404(report_series):
    if not SERIES_NAME_REGEX.match(report_series) or report_series in ('.', '..'):
        raise Http404('Unknown report series')
    series_dir = os.path.join(_autoreports_dir(), report_series)
    if not os.path.isdir(series_dir):
        raise Http404('Unknown report series')
    return series_dir


def _parse_report_filename(filename):
    """Return report info dict for a valid report filename, else None."""
    match = REPORT_FILENAME_REGEX.match(filename)
    if match is None:
        return None
    report_date = match['report_date']       # YYYYMMDD
    creation_date = match['creation_date']   # YYYYMMDDHHMM
    return {
        'filename': filename,
        # keys sortable as strings (lexicographic == chronological for these formats)
        'report_date': report_date,
        'creation_date': creation_date,
        'report_date_iso': f'{report_date[:4]}-{report_date[4:6]}-{report_date[6:]}',
        'indicator': match['indicator'],
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def get_report_series_list(request):
    """List available report series (= subdirectories of AUTOREPORTS_DIR)."""
    reports_dir = _autoreports_dir()
    if not reports_dir or not os.path.isdir(reports_dir):
        return JsonResponse([], safe=False)
    series = sorted(
        entry.name for entry in os.scandir(reports_dir) if entry.is_dir()
    )
    return JsonResponse(series, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_reports(request, report_series):
    """
    List reports of a series, newest first.
    If several reports exist for the same report_date, only the one with the
    latest creation_date is returned.
    """
    series_dir = _get_series_dir_or_404(report_series)

    latest_per_date = {}
    for entry in os.scandir(series_dir):
        if not entry.is_file():
            continue
        report = _parse_report_filename(entry.name)
        if report is None:
            continue  # ignore files not following the naming convention
        current = latest_per_date.get(report['report_date'])
        if current is None or report['creation_date'] > current['creation_date']:
            latest_per_date[report['report_date']] = report

    reports = sorted(
        latest_per_date.values(),
        key=lambda r: r['report_date'],
        reverse=True,
    )
    return JsonResponse(reports, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_report_file(request, report_series, filename):
    """Serve a single report PDF inline."""
    series_dir = _get_series_dir_or_404(report_series)

    # filename must follow the naming convention -> also blocks path traversal
    if REPORT_FILENAME_REGEX.match(filename) is None:
        raise Http404('Unknown report')

    file_path = os.path.join(series_dir, filename)
    if not os.path.isfile(file_path):
        raise Http404('Unknown report')

    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response