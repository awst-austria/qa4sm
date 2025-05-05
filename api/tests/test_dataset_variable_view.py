import logging

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from api.tests.test_helper import *


class TestDatasetVariableView(TestCase):
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables', 'users']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_dataset_variable(self):
        # check if all variables are taken
        dataset_variable_url = reverse('Dataset variable')
        response = self.client.get(dataset_variable_url)
        assert response.status_code == 200
        assert len(response.json()) > 0

        # check availability after logging out
        self.client.logout()

        response = self.client.get(dataset_variable_url)
        assert response.status_code == 200
        assert len(response.json()) > 0

    def test_dataset_variable_by_id(self):
        dataset_variable_url = reverse('Dataset variable')
        # check if they are properly taken based on a variable id given
        response = self.client.get(f'{dataset_variable_url}/1')  # C3S_sm
        assert response.status_code == 200
        assert response.json()['pretty_name'] == 'C3S_sm'

        response = self.client.get(f'{dataset_variable_url}/100')  # wrong id
        assert response.status_code == 404

        # check availability after logging out
        self.client.logout()
        response = self.client.get(f'{dataset_variable_url}/1')  # C3S_sm
        assert response.status_code == 200

    def test_dataset_variable_by_version(self):
        dataset_variable_by_dataset_url_name ='Dataset_variable_by_version'
        # check if they are properly taken based on a dataset id provided
        response = self.client.get(reverse(dataset_variable_by_dataset_url_name, kwargs={'version_id': 5}))  # GLDAS
        assert response.status_code == 200
        assert len(response.json()) == 4  # usually there is only 1, but GLDAS has 4

        response = self.client.get(reverse(dataset_variable_by_dataset_url_name, kwargs={'version_id': 1}))  # C3S
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = self.client.get(reverse(dataset_variable_by_dataset_url_name, kwargs={'version_id': 100}))  # wrong id
        assert response.status_code == 404

        # check availability after logging out
        self.client.logout()

        response = self.client.get(reverse(dataset_variable_by_dataset_url_name, kwargs={'dataset_id': 5}))  # GLDAS
        assert response.status_code == 200


