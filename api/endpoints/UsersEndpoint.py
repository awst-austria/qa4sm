from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.serializers.serializers import UserSerializer
from validator.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_get(request):
    if request.user.is_superuser:
        print('super')

    user = User.objects.all()[:1].get()
    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signup_post(request):
    print(request)
