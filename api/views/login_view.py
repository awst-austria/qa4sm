from django.contrib import auth
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import DateTimeField, CharField
from django_countries.serializer_fields import CountryField
from validator.models import User

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

        # serializer.data #to object

        login_serializer = LoginDtoSerializer(data=request.data)
        if not login_serializer.is_valid():
            return resp_invalid_credentials

        login_data = login_serializer.create()

        user = auth.authenticate(username=login_data.username, password=login_data.password)

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



class UserSerializer(ModelSerializer):
    last_login = DateTimeField(read_only=True)
    date_joined = DateTimeField(read_only=True)
    password = CharField(write_only=True)
    country = CountryField()

    class Meta:
        model = User
        fields = ['username',
                  'password',
                  'email',
                  'first_name',
                  'last_name',
                  'organisation',
                  'last_login',
                  'date_joined',
                  'country',
                  'orcid',
                  'id',
                  'copied_runs',
                  'space_limit',
                  'space_limit_value',
                  'space_left',
                  'is_staff',
                  'is_superuser',
                  'auth_token']