# username = self.kwargs['username']
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def path_var_get(request, **kwargs):
    print('asdf')
    if request.user.is_superuser:
        print('super')
    print(request.user)
    print('asdf')

    print(request.GET)

    return Response(kwargs, status=status.HTTP_200_OK)
