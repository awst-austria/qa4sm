import logging

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from api.tests.test_helper import *
from django.conf import settings


class TestLocalApiView(TestCase):
    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_get_list_of_countries(self):
        country_list_url = reverse('List of countries')
        response = self.client.get(country_list_url)
        assert response.status_code == 200

        self.client.logout()
        response = self.client.get(country_list_url)
        assert response.status_code == 200


