import logging

from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *


class TestDatasetVariableView(TestCase):

    __logger = logging.getLogger(__name__)
    databases = '__all__'
    allow_database_queries = True
    fixtures = ['datasets', 'filters', 'versions', 'variables']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_dataset_variable(self):
        # check if all variables are taken
        response = self.client.get('/api/dataset-variable')
        assert response.status_code == 200
        assert len(response.json()) == 14 # now we have 14, when we merge HR will be more

        # check if they are properly taken based on a dataset id provided
        response = self.client.get('/api/dataset-variable?dataset=5') #GLDAS
        assert response.status_code == 200
        assert len(response.json()) == 4 # usually there is only 1, but GLDAS has 4

        response = self.client.get('/api/dataset-variable?dataset=1') #C3S
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = self.client.get('/api/dataset-variable?dataset=100') # wrong id
        assert response.status_code == 404

        # check if they are properly taken based on a variable id given
        response = self.client.get('/api/dataset-variable?variable_id=1') # C3S_sm
        assert response.status_code == 200
        assert response.json()['short_name'] == 'C3S_sm'

        response = self.client.get('/api/dataset-variable?variable_id=100') # wrong id
        assert response.status_code == 404

        # check availability after logging out
        self.client.logout()

        response = self.client.get('/api/dataset-variable')
        assert response.status_code == 200
        assert len(response.json()) == 14

        response = self.client.get('/api/dataset-variable?dataset=5') #GLDAS
        assert response.status_code == 200

        response = self.client.get('/api/dataset-variable?dataset=100') # wrong id
        assert response.status_code == 404

        response = self.client.get('/api/dataset-variable?variable_id=1') # C3S_sm
        assert response.status_code == 200



