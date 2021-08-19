import logging

from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *


class TestDatasetVersionEndpoint(TestCase):
    __logger = logging.getLogger(__name__)
    databases = '__all__'
    allow_database_queries = True
    fixtures = ['datasets', 'filters', 'versions', 'variables']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_dataset_version(self):
        # check all the versions
        response = self.client.get('/api/dataset-version')
        assert response.status_code == 200
        assert len(response.json()) == 25

        # check for logged out
        self.client.logout()

        response = self.client.get('/api/dataset-version')
        assert response.status_code == 200
        assert len(response.json()) == 25

    def test_dataset_version_by_dataset(self):
        # check versions based on the given dataset
        response = self.client.get('/api/dataset-version-by-dataset/1')  # C3S
        assert response.status_code == 200
        assert len(response.json()) == 4  # there are 4 C3S versions currently

        # check wrong dataset id
        response = self.client.get('/api/dataset-version-by-dataset/100')  # wrong
        assert response.status_code == 404

        # check for logged out
        self.client.logout()

        response = self.client.get('/api/dataset-version-by-dataset/1')  # C3S
        assert response.status_code == 200

    def test_dataset_version_by_id(self):
        # check version id:
        response = self.client.get('/api/dataset-version/1')
        assert response.status_code == 200
        assert response.json()['short_name'] == 'C3S_V201706'

        response = self.client.get('/api/dataset-version/1000')  # wrong version id
        assert response.status_code == 404

        # check for logged out
        self.client.logout()

        response = self.client.get('/api/dataset-version/1')
        assert response.status_code == 200
