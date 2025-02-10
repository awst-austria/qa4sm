import logging

from django.http import JsonResponse
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Exception handler to catch unhandled exceptions.
    Default behavior is to send back the whole stack trace to the rest client which is a security issue so we need to
    override it.

    Parameters
    ----------
    exc
    context

    Returns
    -------
    response
    """
    __logger = logging.getLogger(__name__)
    response = exception_handler(exc, context)
    if response is None:
        __logger.error('Unhandled exception: %s', exc)
        return JsonResponse({'message': 'Unexpected error'}, status=500)

    return response
