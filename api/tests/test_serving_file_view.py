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


def get_ncfile_name(validation):
    file_name_parts = []
    for ind, dataset_config in enumerate(validation.dataset_configurations.all()):
        file_name_parts.append(str(ind) + '-' + dataset_config.dataset.short_name + '.' + dataset_config.variable.pretty_name)
    return ' with '.join(file_name_parts)


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

    def test_get_results(self):
        get_results_url = reverse('Download results')

        # check what happens if there are no files produced
        response = self.client.get(get_results_url + f'?validationId={self.run_id}&fileType=netCDF')
        assert response.status_code == 404
        assert response.content.decode('UTF-8') == 'Given validation has no output directory assigned'

        self.run.output_file = str(self.run_id) + '/' + get_ncfile_name(self.run)
        self.run.save()

        response = self.client.get(get_results_url + f'?validationId={self.run_id}&fileType=netCDF')
        assert response.status_code == 404
        assert 'No such file or directory' in response.content.decode('UTF-8')

        self.run.output_file = ''
        self.run.save()

        # run the validation and generate files
        val.run_validation(self.run_id)
        time.sleep(5)
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

    def test_get_metric_names_and_associated_files(self):
        get_metric_url = reverse('Get metric and plots names')

        response = self.client.get(get_metric_url+f'?validationId={self.run_id}')
        assert response.status_code == 200
        assert response.json()  # checking only if it's not empty; length depends on the number of metrics we use so
        # it doesn't make sense to check it here
