import logging

import validator.validation as val
from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *


class TestDatasetConfigurationView(TestCase):
    __logger = logging.getLogger(__name__)
    databases = '__all__'
    allow_database_queries = True
    fixtures = ['datasets', 'filters', 'versions', 'variables']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_dataset_configuration(self):
        # here I need a validation to check if there are actually any configurations
        run = default_parameterized_validation(self.test_user)
        run.save()
        run_id = run.id
        val.run_validation(run_id)

        response = self.client.get('/api/dataset-configuration')
        assert response.status_code == 200
        assert len(
            response.json()) == 2  # there should be 2, because there was only one validation with 2 datasets used

        response = self.client.get(f'/api/dataset-configuration?validationrun={run_id}')
        assert response.status_code == 200
        assert len(response.json()) == 2  # there should be 2, there are 2 datasets in this validation

        # non-existing validation
        response = self.client.get(f'/api/dataset-configuration?validationrun=1')
        assert response.status_code == 500

        # now I log out the user to check if I can still get the data (assertion as above)
        self.client.logout()
        response = self.client.get('/api/dataset-configuration')
        assert response.status_code == 200
        assert len(response.json()) == 2

        delete_run(ValidationRun.objects.get(pk=run_id))
