import io
import logging
import shutil
import time
from os import path

import pytest
from django.test.utils import override_settings
from django.urls import reverse

import validator.validation as val
from django.test import TestCase
from rest_framework.test import APIClient

from api.tests.test_helper import *
from validator.forms import PublishingForm
from validator.models import ValidationRun
from dateutil import parser
import netCDF4 as nc
from validator.validation import mkdir_if_not_exists, set_outfile

User = get_user_model()


class TestServingFileView(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters']
    __logger = logging.getLogger(__name__)

    def setUp(self):
        # creating the main user to run a validation
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

        self.run = default_parameterized_validation_to_be_run(self.test_user)
        self.run.save()
        self.run_id = self.run.id
        self.wrong_id = 'f0000000-a000-b000-c000-d00000000000'
        val.run_validation(self.run_id)
        time.sleep(5)

    def test_get_results(self):
        get_results_url = reverse('Download results')
        # finished_run = ValidationRun.objects.get(pk=self.run_id)

        # get netCDF
        response = self.client.get(get_results_url+f'?validationId={self.run_id}&fileType=netCDF')
        assert response.status_code == 200
        assert 'netcdf' in response.get('Content-Type')

        # get graphics
        response = self.client.get(get_results_url+f'?validationId={self.run_id}&fileType=graphics')
        assert response.status_code == 200
        assert 'zip' in response.get('Content-Type')

        # get some other file type
        response = self.client.get(get_results_url+f'?validationId={self.run_id}&fileType=some_other_file')
        assert response.status_code == 404

        # get wrong id
        response = self.client.get(get_results_url+f'?validationId={self.wrong_id}&fileType=graphics')
        assert response.status_code == 404

        # log out the user and check everything one more time - should work the same
        self.client.logout()

        # get netCDF
        response = self.client.get(get_results_url+f'?validationId={self.run_id}&fileType=netCDF')
        assert response.status_code == 200
        assert 'netcdf' in response.get('Content-Type')

        # get graphics
        response = self.client.get(get_results_url+f'?validationId={self.run_id}&fileType=graphics')
        assert response.status_code == 200
        assert 'zip' in response.get('Content-Type')

        # get some other file type
        response = self.client.get(get_results_url+f'?validationId={self.run_id}&fileType=some_other_file')
        assert response.status_code == 404

        # get wrong id
        response = self.client.get(get_results_url+f'?validationId={self.wrong_id}&fileType=graphics')
        assert response.status_code == 404

    def test_get_csv_with_statistics(self):
        get_csv_url = reverse('Download statistics csv')

        # everything ok
        response = self.client.get(get_csv_url+f'?validationId={self.run_id}')
        assert response.status_code == 200
        assert 'Stats_summary.csv' in response.get('Content-Disposition')

        # wrong ID
        response = self.client.get(get_csv_url+f'?validationId={self.wrong_id}')
        assert response.status_code == 404

        # log out the user and check one more time
        self.client.logout()
        # everything ok
        response = self.client.get(get_csv_url+f'?validationId={self.run_id}')
        assert response.status_code == 200
        assert 'Stats_summary.csv' in response.get('Content-Disposition')

        # wrong ID
        response = self.client.get(get_csv_url+f'?validationId={self.wrong_id}')
        assert response.status_code == 404
