import datetime
import json
import logging

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient

from api.views.UserCRUDView import UserSignupDto, UserSignupSerializer, UserSerializer
from api.tests.test_helper import create_test_user

User = get_user_model()


class TestUserView(TestCase):
    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()

        self.client = APIClient()
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_user_serializer(self):
        # create a serializer for transforming a User model to json
        model_to_json_serializer = UserSerializer(self.test_user)

        # get json
        user_json = JSONRenderer().render(model_to_json_serializer.data).decode("utf-8")
        assert 'password' not in user_json
        assert self.auth_data['username'] in user_json

    def test_user_signup_serializer(self):
        # prepare a Signup Dto
        user_data = UserSignupDto(
            last_name='john',
            first_name='john',
            organisation='sdfgsdfgstrsdf',
            country='Austria',
            orcid='123546521',
            email='john@john.com',
            username='john88',
            terms_consent='True',
            password='johnspwd',
            last_login=datetime.datetime.now())

        # create a serializer for transforming a dto to json
        dto_to_json_serializer = UserSignupSerializer(user_data)

        json_val = JSONRenderer().render(dto_to_json_serializer.data).decode("utf-8")

        # make sure the password is left out. this is important because clients should not be able to read passwords
        assert 'password' not in json_val

        # map the json string to python dict.
        user_obj = json.loads(json_val)
        # add a password
        user_obj['password'] = 'sdfgsadfasfdawef'
        json_to_dto = UserSignupSerializer(data=user_obj)

        # validate the input dict and create a UserSignupDto
        signup_dto = json_to_dto.create()

        # validate the input dict and create the user in the database
        user_model = json_to_dto.create_model()

        # validate that the user actually has benn created
        assert User.objects.filter(email=signup_dto.email).get()
