import logging

from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *
from django.conf import settings


class TestGlobalParamsView(TestCase):
    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_global_params(self):
        response = self.client.get('/api/globals')
        data = response.json()
        assert response.status_code == 200
        assert data['admin_mail'] == settings.EMAIL_FROM.replace('@', ' (at) ')
        assert data['doi_prefix'] == settings.DOI_URL_PREFIX
        assert data['site_url'] == settings.SITE_URL
        assert data['app_version'] == settings.APP_VERSION
        assert data['expiry_period'] == settings.VALIDATION_EXPIRY_DAYS
        assert data['warning_period'] == settings.VALIDATION_EXPIRY_WARNING_DAYS

        self.client.logout()
        response = self.client.get('/api/globals')
        assert response.status_code == 200
