import logging

from django.urls import reverse
from validator.models import Settings
from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *


class TestSettingsView(TestCase):
    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_settings(self):
        settings_url = reverse('Settings')
        settings_object = Settings()
        settings_object.maintance_mode = False
        settings_object.news = 'this is a test setting'
        settings_object.save()

        response = self.client.get(settings_url)

        assert response.status_code == 200
        assert len(response.json()) == 1

        # should be also reached by a non logged in user
        self.client.logout()

        response = self.client.get(settings_url)
        assert response.status_code == 200

