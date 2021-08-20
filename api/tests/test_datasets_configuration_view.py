import logging

import pytest
from django.test.utils import override_settings
import validator.validation as val
from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *

@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestDatasetConfigurationView(TestCase):
    __logger = logging.getLogger(__name__)
    # databases = '__all__'
    # allow_database_queries = True
    fixtures = ['datasets', 'filters', 'versions', 'variables']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning")  # ignore pytesmo warnings about missing results
    @pytest.mark.filterwarnings(
        "ignore:read_ts is deprecated, please use read instead:DeprecationWarning")  # ignore pytesmo warnings about read_ts
    def test_dataset_configuration(self):
        # Within this test I test both views: dataset_configuration and dataset_configuration_by_dataset,
        # it's done this way to avoid running a new validation twice

        # here I need a validation to check if there are actually any configurations
        run = default_parameterized_validation(self.test_user)
        run.save()
        run_id = run.id
        val.run_validation(run_id)

        # dataset_configuration view
        response = self.client.get('/api/dataset-configuration')
        assert response.status_code == 200
        assert len(
            response.json()) == 2  # there should be 2, because there was only one validation with 2 datasets used

        # dataset_configuration_by_dataset
        response = self.client.get(f'/api/dataset-configuration/{run_id}')
        assert response.status_code == 200
        assert len(response.json()) == 2  # there should be 2, there are 2 datasets in this validation

        # non-existing validation
        wrong_id = 'f0000000-a000-b000-c000-d00000000000'
        response = self.client.get(f'/api/dataset-configuration/{wrong_id}')
        assert response.status_code == 200
        assert len(response.json()) == 0

        # now I log out the user to check if I can still get the data (assertion as above)
        self.client.logout()
        response = self.client.get('/api/dataset-configuration')
        assert response.status_code == 200
        assert len(response.json()) == 2

        delete_run(ValidationRun.objects.get(pk=run_id))
