import logging
import shutil
import time

from django.conf import settings
from django.urls import reverse

import validator.validation as val
from django.test import TestCase
from rest_framework.test import APIClient

from api.tests.test_helper import *
from validator.validation import mkdir_if_not_exists, set_outfile
from django.test.utils import override_settings
User = get_user_model()


def get_ncfile_name(validation):
    file_name_parts = []
    for ind, dataset_config in enumerate(validation.dataset_configurations.all()):
        file_name_parts.append(str(ind) + '-' + dataset_config.dataset.short_name + '.' + dataset_config.variable.pretty_name)
    return ' with '.join(file_name_parts) + '.nc'


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestServingFileView(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']
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

        delete_run(self.run)

    def test_get_csv_with_statistics(self):
        get_csv_url = reverse('Download statistics csv')

        val.run_validation(self.run_id)
        time.sleep(5)

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

        delete_run(self.run)

    def test_get_metric_names_and_associated_files(self):
        get_metric_url = reverse('Get metric and plots names')

        # checking a validation without output file assigned
        response = self.client.get(get_metric_url+f'?validationId={self.run_id}')
        assert response.status_code == 404
        assert response.json()['message'] == 'Given validation has no output directory assigned'

        # assigning an output file - doesn't matter if the name is right, it's needed to create a directory
        self.run.output_file = str(self.run_id) + '/' + get_ncfile_name(self.run)
        self.run.save()

        # checking what happens if there is an output file but no directory
        response = self.client.get(get_metric_url+f'?validationId={self.run_id}')
        assert response.status_code == 404
        assert 'Output directory does not contain any files.' in response.json()['message']

        # create this root and leave it empty
        file_path = self.run.output_dir_url.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
        mkdir_if_not_exists(file_path)

        # check what happens if there is an empty directory
        response = self.client.get(get_metric_url+f'?validationId={self.run_id}')
        print(response.json())
        assert response.status_code == 404
        assert response.json()['message'] == 'There are no result files in the given directory'

        # removing the path
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)

        # cleaning output
        self.run.output_file = ''
        self.run.save()

        # looking for a non-existing validation
        response = self.client.get(get_metric_url+f'?validationId={self.wrong_id}')
        assert response.status_code == 404

        # running the validation to have appropriate files
        val.run_validation(self.run_id)
        time.sleep(5)

        # now everything should be ok
        response = self.client.get(get_metric_url+f'?validationId={self.run_id}')
        assert response.status_code == 200
        assert response.json()  # checking only if it's not empty; length depends on the number of metrics we use so
        # it doesn't make sense to check it here

        delete_run(self.run)

    def test_get_graphic_files(self):
        get_graphic_files_url = reverse('Get graphic files')

        # no file names provided
        response = self.client.get(get_graphic_files_url)

        assert response.status_code == 404
        assert response.json()['message'] == 'No file names given'

        # get static graphic_files
        files = ['/static/images/home/background.webp', '/static/images/logo/logo_awst.webp']
        new_url = get_graphic_files_url + '?'
        for file_name in files:
            new_url += 'file=' + file_name + '&'
        new_url = new_url.rstrip('&')

        response = self.client.get(new_url)
        assert response.status_code == 200
        assert len(response.json()) == 2

        # try to get only one file
        file = '/static/images/home/background.webp'

        response = self.client.get(get_graphic_files_url+f'?file={file}')
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert type(response.json()) == list

        # log out the user, should work also for any user
        self.client.logout()

        response = self.client.get(new_url)
        assert response.status_code == 200
        assert len(response.json()) == 2


    def test_get_graphic_file(self):
        get_graphic_file_url = reverse('Get graphic file')

        # no file names provided
        response = self.client.get(get_graphic_file_url)

        assert response.status_code == 404
        assert response.json()['message'] == 'No file name given'

        # get static graphic_file
        file = '/static/images/home/background.webp'

        response = self.client.get(get_graphic_file_url+f'?file={file}')
        assert response.status_code == 200
        assert len(response.json()) == 1

        # try to get many files
        files = ['/static/images/home/background.webp', '/static/images/logo/logo_awst.webp']
        new_url = get_graphic_file_url + '?'
        for file_name in files:
            new_url += 'file=' + file_name + '&'
        new_url = new_url.rstrip('&')

        # still should work, but only the first file will be returned
        response = self.client.get(new_url)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert type(response.json()) == dict

        # log out the user, should work also for any user
        self.client.logout()

        response = self.client.get(get_graphic_file_url+f'?file={file}')
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_summary_statistics(self):
        summary_statistics_url = reverse('Summary statistics')

        val.run_validation(self.run_id)
        time.sleep(5)

        # everything ok:
        response = self.client.get(summary_statistics_url + f'?id={self.run_id}')
        assert response.status_code == 200
        assert 'table' in response.content.decode('UTF-8')

        # wrong id:
        response = self.client.get(summary_statistics_url + f'?id={self.wrong_id}')
        assert response.status_code == 404

        # logged out user
        self.client.logout()

        # everything should be ok:
        response = self.client.get(summary_statistics_url + f'?id={self.run_id}')
        assert response.status_code == 200
        assert 'table' in response.content.decode('UTF-8')




