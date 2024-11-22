import logging

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

# Include an appropriate `Authorization:` header on all requests.


User = get_user_model()


class TestLoginView(TestCase):
    # fixtures = ['variables', 'versions', 'datasets', 'filters']

    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.auth_data = {
            'username': 'chuck_norris',
            'password': 'roundhousekick',
            'email': 'norris@awst.at'
        }

        self.user_data = {
            'username': self.auth_data['username'],
            'password': self.auth_data['password'],
            'email': self.auth_data['email'],
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'organisation': 'Texas Rangers',
            'country': 'US',
            'orcid': '0000-0002-1825-0097',
        }
        self.client = APIClient()
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.test_user = User.objects.create_user(**self.user_data)
        self.pwd = 'roundhousekick'

    def test_login(self):
        login_url = reverse('api-login')
        # Try to login with wrong password
        response = self.client.post(login_url,
                                    {'identifier': self.auth_data['username'], 'password': 'wrong password'},
                                    format='json')
        assert response.status_code == 401

        # Try to login with username and correct password
        response = self.client.post(login_url,
                                    {'identifier': self.auth_data['username'], 'password': self.auth_data['password']},
                                    format='json')
        # Http response status should be OK(200)
        assert response.status_code == 200

        # Try to login with email and correct password
        response = self.client.post(login_url,
                                    {'identifier': self.auth_data['email'], 'password': self.auth_data['password']},
                                    format='json')
        # Http response status should be OK(200)
        assert response.status_code == 200
