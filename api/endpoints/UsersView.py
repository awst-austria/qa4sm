from django_countries.serializer_fields import CountryField
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.fields import DateTimeField, CharField
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from api.Dto import Dto
from validator.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users(request):
    if request.user.is_superuser:
        print('super')

    user = User.objects.all()[:1].get()
    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signup_post(request):
    print(request)


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
                  'orcid', ]


class UserDto(Dto):
    """
    User DTO with the necessary model fields
    """

    def __init__(self, **kwargs):
        attributes = {'username', 'email', 'first_name', 'last_name', 'organisation', 'country', 'orcid', 'date_joined',
                      'last_login'}
        self.__create_attrs__(attributes)
        for key, value in kwargs.items():
            if key in attributes:
                setattr(self, key, value)


class UserSignupDto(UserDto):
    """
    DTO for user sign up
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        attributes = {'terms_consent'}
        self.__create_attrs__(attributes)

        for key, value in kwargs.items():
            if key in attributes:
                setattr(self, key, value)


class UserSignupSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    organisation = serializers.CharField()
    country = serializers.CharField()
    orcid = serializers.CharField()
    terms_consent = serializers.BooleanField(required=True)
    date_joined = serializers.DateField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserSignupDto

    def create_model(self):
        self.is_valid(raise_exception=True)
        user_data = self.validated_data
        user_data.pop('terms_consent', None)
        return User.objects.create_user(**user_data)

    def create(self):
        self.is_valid(raise_exception=True)
        return UserSignupDto(**self.validated_data)

    def update(self, instance, validated_data):
        pass
