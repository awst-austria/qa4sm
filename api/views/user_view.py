from django.db import IntegrityError
from django.http import HttpResponse, QueryDict
from django_countries.serializer_fields import CountryField
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.fields import DateTimeField, CharField
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from validator.mailer import send_new_user_signed_up
from validator.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users(request):
    if request.user.is_superuser:
        print('super')

    user = User.objects.all()
    serializer = UserSerializer(user, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_post(request):
    if request.method == 'POST':
        new_user_data = request.data
        del new_user_data['password2']

        try:
            new_user = UserSerializer().create(new_user_data)
            new_user.is_active = False
            new_user.save()
            send_new_user_signed_up(new_user)
            response = 'New user registered'
        except IntegrityError as e:
            response = str(e)

    return HttpResponse(response, status=200)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def user_update(request):
    user = User.objects.get(username=request.user.username)
    if request.method == 'PATCH':
        user_data = request.data
        del user_data['password2']
        for key in user_data:
            print(key, user_data[key], getattr(user, key))
            if getattr(user, key) != user_data[key]:
                setattr(user, key, user_data[key])
            user.save()
        response = 'User data updated'
        return HttpResponse(response, status=200)


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
                  'copied_runs']
        extra_kwargs = {'password': {"write_only": True, 'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
