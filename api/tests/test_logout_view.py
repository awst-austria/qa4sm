import logging

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

# Include an appropriate `Authorization:` header on all requests.
from api.tests.test_helper import create_test_user

User = get_user_model()


class TestLogoutView(TestCase):
    # fixtures = ['variables', 'versions', 'datasets', 'filters']

    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_logout(self):
        response = self.client.post('/api/auth/logout')
        assert response.status_code == 200
        # logged-out so now the status code should be 403, because this endpoint is restricted
        response = self.client.post('/api/auth/logout')
        assert response.status_code == 403
