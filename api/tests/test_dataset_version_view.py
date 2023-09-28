import logging

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from api.tests.test_helper import *

class TestDatasetVersionView(TestCase):
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables', 'users']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_dataset_version(self):
        dataset_version_url = reverse('Dataset version')
        # check all the versions
        response = self.client.get(dataset_version_url)
        assert response.status_code == 200
        assert len(response.json()) > 0

        # check for logged out
        self.client.logout()

        response = self.client.get(dataset_version_url)
        assert response.status_code == 200
        assert len(response.json()) > 0

    def test_dataset_version_by_dataset(self):
        dataset_version_by_dataset_url_name = 'Dataset version by dataset'
        # check versions based on the given dataset
        response = self.client.get(reverse(dataset_version_by_dataset_url_name, kwargs={'dataset_id': 1}))  # C3S
        assert response.status_code == 200
        assert len(response.json()) == 5  # there are 4 C3S versions currently

        # check wrong dataset id
        response = self.client.get(reverse(dataset_version_by_dataset_url_name, kwargs={'dataset_id': 100}))  # wrong
        assert response.status_code == 404

        # check for logged out
        self.client.logout()

        response = self.client.get(reverse(dataset_version_by_dataset_url_name, kwargs={'dataset_id': 1}))  # C3S
        assert response.status_code == 200

    def test_dataset_version_by_id(self):
        dataset_version_url = reverse('Dataset version')
        # check version id:
        response = self.client.get(f'{dataset_version_url}/1')
        assert response.status_code == 200
        assert response.json()['short_name'] == 'C3S_V201706'

        response = self.client.get(f'{dataset_version_url}/1000')  # wrong version id
        assert response.status_code == 404

        # check for logged out
        self.client.logout()

        response = self.client.get(f'{dataset_version_url}/1')
        assert response.status_code == 200
