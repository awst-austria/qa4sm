from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from validator.models import ValidationRun
from django.conf.urls.static import static
from django.conf import settings


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_results(request):
    validation_id = request.query_params.get('validationId', None)
    file_type = request.query_params.get('fileType', None)
    valrun = get_object_or_404(ValidationRun, pk=validation_id)
    file_path = valrun.output_dir_url.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
    print('filePath:', file_path)
    if file_type == 'netCDF':
        filename = file_path + valrun.output_file_name
    else:
        filename = file_path + 'graphs.zip'
    response = FileResponse(open(filename, 'rb'))
    return response
