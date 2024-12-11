from django.contrib import auth
from django.contrib.auth import login, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from api.views.user_view import UserSerializer

# Predefined response bodies
resp_invalid_credentials = JsonResponse({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
resp_unauthorized = JsonResponse({'message': 'Unauthorized :-('}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def api_login(request):
    """
    Authentication endpoint that handles login requests.

    POST:
        Login request
        Request body: LoginDto

    GET:
        Response body: User object if logged in. Otherwise HTTP-401(Unauthorized)
    """
    if request.method == 'POST':

        login_serializer = LoginDtoSerializer(data=request.data)
        if not login_serializer.is_valid():
            return resp_invalid_credentials

        login_data = login_serializer.create()

        if '@' in login_data.identifier:
            # django authenticate method can only take username, not email
            try:
                username = get_user_model().objects.get(email=login_data.identifier).username
                user = auth.authenticate(username=username, password=login_data.password)
            except get_user_model().DoesNotExist:
                return resp_invalid_credentials
        else: 
            user = auth.authenticate(username=login_data.identifier, password=login_data.password)

        if user:
            if user is not None:
                login(request, user)
                user_serializer = UserSerializer(request.user)
                return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)

        return resp_invalid_credentials

    elif request.method == 'GET':
        cookies = request.COOKIES
        headers = request.headers
        if request.user.is_authenticated:
            user_serializer = UserSerializer(request.user)
            return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return resp_unauthorized


class LoginDto(object):
    """
    DTO for login requests
    """

    def __init__(self, identifier='', password=''):
        self.identifier = identifier
        self.password = password


class LoginDtoSerializer(serializers.Serializer):
    def create(self):
        return LoginDto(identifier=self.validated_data['identifier'], password=self.validated_data['password'])

    def update(self, instance):
        pass

    identifier = serializers.CharField(min_length=1)
    password = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        model = LoginDto
