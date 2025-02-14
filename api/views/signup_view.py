from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.dto import Dto

User = get_user_model()


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
    """
    We need an extra serializer for signup because of the "terms_consent" field.
    Unfortunately a ModelSerializer cannot handle extra attributes on top of those that are defined in the model.
    Since the "terms_consent" field is not part of the User model but must be part of the signup form, the
    UserModelSerializer cannot be used for signup.
    """
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=True, unique=True, validators=[UniqueValidator(queryset=User.objects.all(), message="This username is already in use.")])
    email = serializers.EmailField(required=True, unique=True, validators=[UniqueValidator(queryset=User.objects.all(), message="This email is already in use, if you require help please contact the adminisators.")])
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    organisation = serializers.CharField()
    country = serializers.CharField()
    orcid = serializers.CharField(unique=True, validators=[UniqueValidator(queryset=User.objects.all(), message="This ORCID is already in use, if you require help please contact the adminisators.")])
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
