from django.contrib import auth
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, serializers, authentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def api_login(request):
    """
    Authentication endpoint POST: Request body: {"username":"username","password":"password"}

    GET:
        Response body: User object if logged in. Otherwise HTTP-401(Unauthorized)
    """
    if request.method == 'POST':

        # serializer.data #to object

        login_serializer = LoginDtoSerializer(data=request.data)
        if not login_serializer.is_valid():
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        login_data = login_serializer.create()

        user = auth.authenticate(username=login_data.username, password=login_data.password)

        if user:
            if user is not None:
                login(request, user)
                return JsonResponse({"detail": "Success"})

        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'GET':
        if request.user.is_authenticated:
            return JsonResponse({"message": "Authenticated"})
        else:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class LoginDto(object):
    def __init__(self, username='', password=''):
        self.username = username
        self.password = password


class LoginDtoSerializer(serializers.Serializer):
    def create(self):
        return LoginDto(username=self.validated_data['username'], password=self.validated_data['password'])

    def update(self, instance):
        pass

    username = serializers.CharField(min_length=1)
    password = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        model = LoginDto
