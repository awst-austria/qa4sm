import logging

from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *


class TestDatasetView(TestCase):
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_dataset(self):
        response = self.client.get('/api/dataset')
        assert response.status_code == 200
        assert len(response.json()) == 11

        self.client.logout()

        response = self.client.get('/api/dataset')
        assert response.status_code == 200

    def dataset_by_id(self):
        response = self.client.get('/api/dataset/1')
        assert response.status_code == 200
        assert response.json()['pretty_name'] == 'C3S'

        response = self.client.get('/api/dataset/100')  # wrong id
        assert response.status_code == 404

        self.client.logout()
        response = self.client.get('/api/dataset/1')
        assert response.status_code == 200
