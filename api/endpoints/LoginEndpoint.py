import datetime
import json

from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from django.contrib import auth
from django.conf import settings
import jwt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers.serializers import UserSerializer

# class Login(GenericAPIView):
from validator.admin import User

JWT_REFRESH_TOKEN_NAME = 'jwt_refresh_token'


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_post(request):
    """
    Authentication endpoint
    Request body: {"username":"username","password":"password"}
    Response: JWT token
    """
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user:
        jwt_token = 'JWT ' + jwt.encode({'username': user.username, 'iat': datetime.datetime.now()},
                                        settings.API_SECRET_KEY,
                                        algorithm=settings.JWT_ALGORYTHM)
        refresh_token = 'JWT ' + jwt.encode({'username': user.username, 'iat': datetime.datetime.now()},
                                            settings.API_SECRET_KEY,
                                            algorithm=settings.JWT_ALGORYTHM)
        user_serializer = UserSerializer(user)
        data = {'user': user_serializer.data, 'token': jwt_token}
        response = HttpResponse(json.dumps(data), status=status.HTTP_200_OK)
        response.set_cookie(JWT_REFRESH_TOKEN_NAME, refresh_token,
                            expires=datetime.datetime.now() + datetime.timedelta(
                                hours=settings.JWT_REFRESH_TOKEN_LIFETIME),
                            httponly=True)
        return response

    return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LoginReqDto(object):
    def __init__(self, username='', password=''):
        self.username = username
        self.password = password


class LoginDtoSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = LoginReqDto
        fields = ['username', 'password']

    def validate(self, attrs):
        if User.objects.filter(email=attrs['username']).exists():
            raise serializers.ValidationError({'email', 'Email already exists'})
        return super.validate(attrs)

    def create(self, validated_dto):
        return User.objects.create_user(validated_dto)


class LoginRespDto(object):
    def __init__(self, username, token):
        self.username = username
        self.token = token

# class LoginDtoSerializer(serializers.ModelSerializer):
#     username = serializers.CharField()
#     username_error = serializers.CharField()
#     password = serializers.CharField(write_only=True)
#     password_error = serializers.CharField()
#
#     # email = serializers.EmailField()
#
#     class Meta:
#         model = LoginDto
#         fields = ['username', 'username_error', 'password', 'password_error']
#
#     def validate(self, attrs):
#         if User.objects.filter(email=attrs['email']).exists():
#             raise serializers.ValidationError({'email', 'Email already exists'})
#         return super.validate(attrs)
#
#     def create(self, validated_dto):
#         return User.objects.create_user(validated_dto)
