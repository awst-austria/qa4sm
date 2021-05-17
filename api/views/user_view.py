from django.contrib.auth import logout
from django.db import IntegrityError
from django.http import HttpResponse, QueryDict
from django_countries.serializer_fields import CountryField
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.fields import DateTimeField, CharField
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from validator.mailer import send_new_user_signed_up, send_user_account_removal_request, send_user_status_changed
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
        try:
            new_user = UserSerializer().create(new_user_data)
            new_user.is_active = False
            new_user.save()
            send_new_user_signed_up(new_user)
            response = 'New user registered'
        except IntegrityError as e:
            response = str(e)

    return HttpResponse(response, status=200)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_modify(request):
    # this one serves for both, updating and deactivating user
    user = User.objects.get(username=request.user.username)
    if request.method == 'PATCH':
        user_data = request.data
        updated_user = UserSerializer().update(user, user_data)
        return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        request.user.is_active = False
        request.user.save()
        send_user_account_removal_request(request.user)
        send_user_status_changed(request.user,False)
        logout(request)
        return HttpResponse(status=200)



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

    @staticmethod
    def validate_password(validated_data):
        if validated_data['password2'] == validated_data['password']:
            del validated_data['password2']
        else:
            raise IntegrityError('Passwords do not match')

        return validated_data

    def create(self, validated_data):
        cleaned_data = self.validate_password(validated_data)
        user = User.objects.create_user(**cleaned_data)
        return user

    def update(self, instance, validated_data):
        cleaned_data = self.validate_password(validated_data)
        password = cleaned_data.pop('password', None)

        for (key, value) in cleaned_data.items():
            setattr(instance, key, value)

        if password is not None and password != '':
            instance.set_password(password)

        instance.save()

        return instance
