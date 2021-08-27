import logging

from django.urls import reverse

import validator.validation as val
from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *


class TestValidationRunView(TestCase):
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.second_user_data, self.second_test_user = create_alternative_user()


        self.client = APIClient()
        self.client.login(**self.auth_data)

        self.run = create_default_validation_without_running(self.test_user)
        self.run.name_tag = 'B validation'
        self.run.save()

        self.run_2 = create_default_validation_without_running(self.second_test_user)
        self.run_2.name_tag = 'A validation'
        self.run_2.save()

    def test_published_results(self):
        published_results_url = reverse('Published results')

        # 'publishing' results
        self.run.doi = '12345/12434'
        self.run.save()
        self.run_2.doi = '108645/12434'
        self.run_2.save()

        response = self.client.get(published_results_url)
        assert response.status_code == 200
        assert len(response.json()['validations']) == 2

        # introducing limit and offset
        response = self.client.get(published_results_url+f'?limit=1&offset=0')
        assert response.status_code == 200
        assert len(response.json()['validations']) == 1 # now there should be only one taken

        # introducing order
        response = self.client.get(published_results_url + f'?order=-name_tag')
        print(response.json()['validations'])
        assert response.status_code == 200
        assert response.json()['validations'][0]['name_tag'] == 'B validation'
        assert response.json()['validations'][1]['name_tag'] == 'A validation'

        # changing the order
        response = self.client.get(published_results_url + f'?order=name_tag')
        print(response.json()['validations'])
        assert response.status_code == 200
        assert response.json()['validations'][0]['name_tag'] == 'A validation'
        assert response.json()['validations'][1]['name_tag'] == 'B validation'




