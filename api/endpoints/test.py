from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.serializers.serializers import UserSerializer
from validator.models import User


class TestEndpoint(GenericAPIView):
    serializer_class = UserSerializer

    def get(self, request):
        user = User.objects.all()[:1].get()
        serializer = UserSerializer(user)
        print(request.GET)
        print(request.GET['cucc'])
        return Response(serializer.data, status=status.HTTP_200_OK)
