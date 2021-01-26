from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from django.contrib import auth
from django.conf import settings
import jwt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers.serializers import UserSerializer


# class Login(GenericAPIView):
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
        jwt_token = jwt.encode({'username': user.username}, settings.API_SECRET_KEY, algorithm=settings.JWT_ALGORYTHM)
        user_serializer = UserSerializer(user)
        data = {
            'user': user_serializer.data,
            'token': jwt_token
        }
        return Response(data, status=status.HTTP_200_OK)

    return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
