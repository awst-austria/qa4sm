import logging

from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
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
        assert len(response.json()) == 6  # there at least 6 C3S versions currently

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

    def test_dataset_version_update(self):
        dataset_version_url_update = reverse('Update Dataset Version')
        version_data = [{"id": "1", "time_range_end": "2022-10-10"}, {"id": "2", "time_range_end": "2023-02-15"}]

        response = self.client.post(dataset_version_url_update, version_data, format='json')

        assert response.status_code == 401  # can not send request without a token
        # create a token
        token, created = Token.objects.get_or_create(user=self.test_user)
        assert created

        # authorization method changed
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.post(dataset_version_url_update, version_data, format='json')
        assert response.status_code == 403  # still not admin user, but this time 403,
        # because with token authentication it throws 403 instead of 401

        #  add admin user credentials
        self.test_user.is_superuser = True
        self.test_user.is_staff = True
        self.test_user.save()

        response = self.client.post(dataset_version_url_update, version_data, format='json')
        assert response.status_code == 200  # still no admin user

        version_1 = DatasetVersion.objects.get(id=1)
        version_2 = DatasetVersion.objects.get(id=2)

        assert version_1.time_range_end == version_data[0].get('time_range_end')
        assert version_2.time_range_end == version_data[1].get('time_range_end')

        # not existing data
        version_data_incorrect = [{"id": "100", "time_range_end": "2022-10-10"},
                                  {"id": "2", "time_range_end": "2023-02-15"}]

        response = self.client.post(dataset_version_url_update, version_data_incorrect, format='json')
        assert response.status_code == 404

        # not existing field
        version_data_incorrect = [{"id": "1", "time_range_": "2022-10-10"},
                                  {"id": "2", "time_range_end": "2023-02-15"}]

        response = self.client.post(dataset_version_url_update, version_data_incorrect, format='json')
        assert response.status_code == 500
