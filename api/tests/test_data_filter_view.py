import logging

import validator.validation as val
from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *


class TestDataFilterView(TestCase):
    __logger = logging.getLogger(__name__)
    databases = '__all__'
    allow_database_queries = True
    fixtures = ['datasets', 'filters', 'versions', 'variables']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_data_filter(self):
        # all filters
        response = self.client.get('/api/data-filter')

        assert response.status_code == 200
        # currently we have 23 filters, for some reason we don't have a filter with id = 8
        assert len(response.json()) == 23

        # check filters for C3S (id = 1)
        dataset_id = 1  #
        response = self.client.get(f'/api/data-filter?dataset={dataset_id}')
        assert response.status_code == 200
        assert len(response.json()) == 6

        # log out to check if it still works
        self.client.logout()
        # all filters
        response = self.client.get('/api/data-filter')
        assert response.status_code == 200
        # currently we have 23 filters, for some reason we don't have a filter with id = 8
        assert len(response.json()) == 23

    def test_data_parameterized_filters(self):
        # here I need a validation to check if there are actually parameterised filters
        run = default_parameterized_validation(self.test_user)
        run.save()
        run_id = run.id
        val.run_validation(run_id)
        new_run = ValidationRun.objects.get(pk=run_id)
        new_run_ref_config = DatasetConfiguration.objects.get(pk=new_run.reference_configuration_id)

        # all filters
        response = self.client.get('/api/param-filter')
        assert response.status_code == 200
        assert len(
            response.json()) == 2  # there will be only 2, as there has been only one validation run with 2 param filters applied

        # filters assigned to the particular config
        response = self.client.get(f'/api/param-filter?config={new_run_ref_config.id}')
        assert response.status_code == 200
        assert len(response.json()) == 2  # there will be only 2, as there are 2 assigned to this particular config
        assert response.json()[0]['parameters'] == 'SCAN'
        assert response.json()[1]['parameters'] == '0.0,0.1'

        # checking for non-existing config
        response = self.client.get(f'/api/param-filter?config={100}')
        assert response.status_code == 404

        # now I log out the user to check if I can still get the data (assertion as above)
        self.client.logout()
        response = self.client.get('/api/param-filter')
        assert response.status_code == 200
        assert len(response.json()) == 2

        # cleaning up
        delete_run(new_run)
