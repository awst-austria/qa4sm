import logging

from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *


class TestDataFilterView(TestCase):
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

        self.run = create_default_validation_without_running(self.test_user)
        self.run.save()
        self.run_id = self.run.id

    def test_data_filter(self):
        # all filters
        data_filter_url = reverse('Dataset filters')
        response = self.client.get(data_filter_url)

        assert response.status_code == 200
        # currently, we have 31 filters, for some reason we don't have a filter with id = 8
        assert len(response.json()) == 33

        # log out to check if it still works
        self.client.logout()

        response = self.client.get(data_filter_url)
        assert response.status_code == 200
        assert len(response.json()) == 33

    def test_data_filter_by_dataset(self):
        data_filter_url = reverse('Dataset filters')
        # check filters for C3S (id = 1)
        dataset_id = 1  #
        response = self.client.get(f'{data_filter_url}/{dataset_id}')
        assert response.status_code == 200
        assert len(response.json()) == 6

        # log out to check if it still works
        self.client.logout()
        response = self.client.get(f'{data_filter_url}/{dataset_id}')
        assert response.status_code == 200
        assert len(response.json()) == 6

    def test_data_parameterized_filters(self):
        param_filter_url = reverse('Parameterised filter')

        # all filters
        response = self.client.get(param_filter_url)
        assert response.status_code == 200
        # there will be only 2, as there has been only one validation run with 2 param filters applied
        assert len(response.json()) == 2

        # now I log out the user to check if I can still get the data (assertion as above)
        self.client.logout()
        response = self.client.get(param_filter_url)
        assert response.status_code == 200
        assert len(response.json()) == 2

