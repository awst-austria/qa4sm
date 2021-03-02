from validator.context_processors import globals_processor
from django.http import JsonResponse
from rest_framework import status


def global_params(request):
    data = globals_processor(request)
    return JsonResponse(data, status=status.HTTP_200_OK)