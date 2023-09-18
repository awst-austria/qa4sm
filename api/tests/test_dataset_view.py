import logging

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from api.tests.test_helper import *


class TestDatasetView(TestCase):
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables', 'users']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_dataset(self):
        dataset_url = reverse('Datasets')
        response = self.client.get(dataset_url)
        assert response.status_code == 200
        assert len(response.json()) > 0

        self.client.logout()

        response = self.client.get(dataset_url)
        assert response.status_code == 200

    def test_dataset_by_id(self):
        dataset_url = reverse('Datasets')
        response = self.client.get(f'{dataset_url}/1')
        assert response.status_code == 200
        assert response.json()['pretty_name'] == 'C3S SM combined'

        response = self.client.get(f'{dataset_url}/100')  # wrong id
        assert response.status_code == 404

        self.client.logout()
        response = self.client.get(f'{dataset_url}/1')
        assert response.status_code == 200
