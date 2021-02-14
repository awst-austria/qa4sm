import logging

from django.http import JsonResponse


def custom_exception_handler(exc, context):
    __logger = logging.getLogger(__name__)
    # response = exception_handler(exc, context)
    __logger.error('Unhandled exception: ', exc)
    return JsonResponse({'message': 'Unexpected error'}, status=500)
