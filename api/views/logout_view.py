from django.contrib.auth import logout
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """
    Authentication endpoint that handles logout requests.

    POST:
        Logout request

    """
    if request.method == 'POST':
        logout(request)
        return HttpResponse(status=status.HTTP_200_OK)
