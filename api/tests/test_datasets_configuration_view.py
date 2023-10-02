import logging

from django.test.utils import override_settings
from django.urls import reverse

from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *

@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestDatasetConfigurationView(TestCase):
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables', 'users']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

        self.run = create_default_validation_without_running(self.test_user)
        self.run.save()

    def test_dataset_configuration(self):
        # Within this test I test both views: dataset_configuration and dataset_configuration_by_dataset,

        dataset_configuration_url = reverse('Configuration')
        # dataset_configuration view
        response = self.client.get(dataset_configuration_url)
        assert response.status_code == 200
        assert len(
            response.json()) == 2  # there should be 2, because there was only one validation with 2 datasets used

        # dataset_configuration_by_dataset
        response = self.client.get(f'{dataset_configuration_url}/{self.run.id}')
        assert response.status_code == 200
        assert len(response.json()) == 2  # there should be 2, there are 2 datasets in this validation

        # non-existing validation
        wrong_id = 'f0000000-a000-b000-c000-d00000000000'
        response = self.client.get(f'{dataset_configuration_url}/{wrong_id}')
        assert response.status_code == 200
        assert len(response.json()) == 0

        # now I log out the user to check if I can still get the data (assertion as above)
        self.client.logout()
        response = self.client.get(dataset_configuration_url)
        assert response.status_code == 200
        assert len(response.json()) == 2

        response = self.client.get(f'{dataset_configuration_url}/{self.run.id}')
        assert response.status_code == 200
        assert len(response.json()) == 2  # there should be 2, there are 2 datasets in this validation
