import os
import re

from collections import defaultdict

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import redirect

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# <report_date>_<creation_date>[_<indicator>].pdf
# e.g. 20260131_202606290613_G.pdf 

REPORT_FILENAME_REGEX = re.compile(
    r'^(?P<report_date>\d{8})_(?P<creation_date>\d{12})(?:_(?P<indicator>[A-Z]))?\.pdf$'
)
# series = directory name, e.g. SMOS_L2_v700 or 'C3S v202605 Quarterly';
# no slashes, no leading/trailing whitespace
SERIES_NAME_REGEX = re.compile(r'^[A-Za-z0-9][A-Za-z0-9 _.-]*$')


def _autoreports_dir():
    """Resolve AUTOREPORTS_DIR; relative paths are resolved against BASE_DIR (local dev)."""
    reports_dir = getattr(settings, 'AUTOREPORTS_DIR', '')
    if reports_dir and not os.path.isabs(reports_dir):
        reports_dir = os.path.abspath(os.path.join(settings.BASE_DIR, reports_dir))
    return reports_dir


def _get_series_dir_or_404(report_series):
    reports_dir = _autoreports_dir()
    if not reports_dir or not SERIES_NAME_REGEX.match(report_series):
        raise Http404('Unknown report series')
    if report_series != report_series.strip():
        raise Http404('Unknown report series')

    root = os.path.realpath(reports_dir)
    series_dir = os.path.realpath(os.path.join(root, report_series))
    # the resolved path must stay inside AUTOREPORTS_DIR
    if os.path.commonpath([root, series_dir]) != root or series_dir == root:
        raise Http404('Unknown report series')
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
        'indicator': match['indicator'],     # None -> JSON null when no indicator
    }


def _collect_reports(series_dir):
    """
    Collect reports of a series directory, newest first.

    Reports are grouped by report_date: a report date may have been processed
    more than once, and the version with the latest creation_date is the
    current one. Earlier versions are not dropped but attached under
    'previous_versions' (newest first), so that URLs already published in the
    "cite" section of a report stay discoverable in the UI, not just
    reachable by direct link.

    Report files are never removed by this API - the citation guarantee rests
    on the files staying on disk.
    """
    versions_per_date = defaultdict(list)
    for entry in os.scandir(series_dir):
        if not entry.is_file():
            continue
        report = _parse_report_filename(entry.name)
        if report is None:
            continue  # ignore files not following the naming convention
        versions_per_date[report['report_date']].append(report)

    reports = []
    for versions in versions_per_date.values():
        versions.sort(key=lambda r: r['creation_date'], reverse=True)
        current, *previous = versions
        reports.append({**current, 'previous_versions': previous})

    reports.sort(key=lambda r: r['report_date'], reverse=True)
    return reports


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

    One entry per report date - the most recently generated version, with any
    earlier versions of the same report date under 'previous_versions'.
    """
    series_dir = _get_series_dir_or_404(report_series)
    return JsonResponse(_collect_reports(series_dir), safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_report(request, report_series):
    """
    Redirect to the newest report file of a series.

    Stable, shareable URL that data providers can bookmark or fetch without
    knowing the current file name:

        GET /api/autoreports/<series>/latest  ->  302 to the newest file

    Note that this URL is not a citable reference: it points at whatever is
    newest at the time of the request. The "cite" section of a report
    must use the per-file URL.
    """
    series_dir = _get_series_dir_or_404(report_series)
    reports = _collect_reports(series_dir)
    if not reports:
        raise Http404('No reports available for this series')
    # _collect_reports returns newest first
    return redirect(
        'autoreports-file',
        report_series=report_series,
        filename=reports[0]['filename'],
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_report_file(request, report_series, filename):
    """
    Serve a single report PDF inline.

    Any file following the naming convention is served - published citation URLs must keep working after a report date
    has been reprocessed.
    """
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