from django.contrib import auth
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# class Login(GenericAPIView):
from validator.admin import User

JWT_REFRESH_TOKEN_NAME = 'jwt_refresh_token'


@api_view(['POST'])
@permission_classes([AllowAny])
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
        if user is not None:
            login(request, user)
            return JsonResponse({"detail": "Success"})

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
