from validator.context_processors import globals_processor
from django.http import JsonResponse
from rest_framework import status
from django.conf import settings


def global_params(request):
    data = globals_processor(request)
    data['app_version'] = settings.APP_VERSION

    return JsonResponse(data, status=status.HTTP_200_OK)
