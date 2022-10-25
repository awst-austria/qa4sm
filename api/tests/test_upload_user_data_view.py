import logging
from api.tests.test_helper import *
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from validator.models import UserDatasetFile, DataVariable
from django.conf import settings
import shutil
from pathlib import Path


def _create_test_file(path):
    test_file = open(path, 'w')
    test_file.write('some test content of a no netcdf file\n')
    test_file.close()
    test_file = open(path, 'rb')
    return test_file


def _clean_up_data(file_entry):
    datafile = file_entry.file.path
    outdir = os.path.dirname(datafile)
    assert os.path.isfile(datafile)
    file_entry.delete()
    assert not os.path.exists(outdir)


class TestUploadUserDataView(APITestCase):
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.second_user_data, self.second_test_user = create_alternative_user()

        self.client = APIClient()
        self.client.login(**self.auth_data)
        self.user_data_path = os.path.join(settings.BASE_DIR, 'testdata/user_data')
        self.test_user_data_path = f'{self.user_data_path}/{self.test_user.username}'
        Path(self.test_user_data_path).mkdir(exist_ok=True, parents=True)

        self.netcdf_file_name = 'teststack_c3s_2dcoords_min_attrs.nc'
        self.not_netcdf_file_name = 'test_file.txt'

        self.netcdf_file = f'{self.user_data_path}/{self.netcdf_file_name}'
        self.not_netcdf_file = f'{self.user_data_path}/{self.not_netcdf_file_name}'

        self.upload_data_url_name = 'Upload user data'
        self.post_metadata_url_name = 'Post User Data File Metadata'
        self.get_user_data_list_name = "Get User Data Files"

    def _remove_user_datafiles(self, username):
        user_data_path = f'{self.user_data_path}/{username}'
        shutil.rmtree(user_data_path)

    def test_get_list_of_user_data_files(self):
        # post the same file 3 times, to create 3 different entries
        self.client.post(reverse(self.upload_data_url_name, kwargs={'filename': self.netcdf_file_name}),
                         {'file': self.netcdf_file}, format='multipart')
        self.client.post(reverse(self.upload_data_url_name, kwargs={'filename': self.netcdf_file_name}),
                         {'file': self.netcdf_file}, format='multipart')
        self.client.post(reverse(self.upload_data_url_name, kwargs={'filename': self.netcdf_file_name}),
                         {'file': self.netcdf_file}, format='multipart')

        response = self.client.get(reverse(self.get_user_data_list_name))
        existing_files = response.json()

        assert response.status_code == 200
        assert len(existing_files) == 3

        # log out and log in as another user
        self.client.logout()
        self.client.login(**self.second_user_data)

        # there should be no files available
        response = self.client.get(reverse(self.get_user_data_list_name))
        existing_files = response.json()
        assert response.status_code == 200
        assert len(existing_files) == 0

        self.client.logout()
        self.client.login(**self.auth_data)
        assert len(os.listdir(self.test_user_data_path)) == 3
        self._remove_user_datafiles(self.test_user)
        assert not os.path.exists(self.test_user_data_path)

        # there are no files, so there will be an error returned;
        response = self.client.get(reverse(self.get_user_data_list_name))
        assert response.status_code == 500


        # cleaning
        for entry in UserDatasetFile.objects.all():
            entry.delete()

        assert len(UserDatasetFile.objects.all()) == 0

    def test_upload_user_data_correct(self):
        response = self.client.post(reverse(self.upload_data_url_name, kwargs={'filename': self.netcdf_file_name}),
                                    {'file': self.netcdf_file}, format='multipart')

        assert response.status_code == 200

        existing_files = UserDatasetFile.objects.all()

        assert len(existing_files) == 1
        file_entry = existing_files[0]
        file_dir = file_entry.get_raw_file_path

        assert len(os.listdir(self.test_user_data_path)) == 1
        assert os.path.exists(file_dir)

        # metadata hasn't been posted yet, so most of the fields should be empty
        assert file_entry.dataset is None
        assert file_entry.version is None
        assert file_entry.variable is None
        assert file_entry.lon_name is None
        assert file_entry.lat_name is None
        assert file_entry.time_name is None
        assert file_entry.owner == self.test_user
        file_entry.delete()

        # check if the entry got removed along with the entire file directory
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert not os.path.exists(file_dir)
        assert len(os.listdir(self.test_user_data_path)) == 0

    def test_upload_user_data_not_netcdf(self):
        file_to_upload = _create_test_file(self.not_netcdf_file)
        response = self.client.post(reverse(self.upload_data_url_name, kwargs={'filename': self.not_netcdf_file_name}),
                                    {'file': file_to_upload}, format='multipart')
        # assert False
        assert response.status_code == 500

        # checking if nothing got to the db and to the data path
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert len(os.listdir(self.test_user_data_path)) == 0

    def test_upload_user_data_with_wrong_name(self):
        file_to_upload = _create_test_file(self.not_netcdf_file)
        response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={'filename': 'wrong_name'}),
            {'file': file_to_upload}, format='multipart')
        # assert False
        assert response.status_code == 500

        # checking if nothing got to the db and to the data path
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert len(os.listdir(self.test_user_data_path)) == 0

    def test_post_user_file_metadata_and_preprocess_file(self):
        # I am posting the file to create the proper dataset entry
        response = self.client.post(reverse(self.upload_data_url_name, kwargs={'filename': self.netcdf_file_name}),
                                    {'file': self.netcdf_file}, format='multipart')
        assert response.status_code == 200

        # checking if the file entry got saved
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 1

        file_entry = existing_files[0]
        # I need to replace the posted file with the original one, because the api post method somehow corrupts netCDFs
        # which is not the problem when I post them via angular and I don't want to deal with it right now.
        shutil.copy2(self.netcdf_file, file_entry.file.path)

        metadata_correct = {
            'dataset_name': 'test_dataset',
            'dataset_pretty_name': 'test_dataset_pretty_name',
            'version_name': 'test_version',
            'version_pretty_name': 'test_version_pretty_name'
        }
        # posting metadata as those from the metadata form and checking if it has been done
        response_metadata = self.client.post(reverse(self.post_metadata_url_name, kwargs={'file_uuid': file_entry.id}),
                                             metadata_correct, format='json')
        assert response_metadata.status_code == 200

        # re-querying file entry
        file_entry = UserDatasetFile.objects.get(id=response.json()['id'])
        # checking if the posted metadata is proper
        assert file_entry.dataset.short_name == metadata_correct['dataset_name']
        assert file_entry.dataset.pretty_name == metadata_correct['dataset_pretty_name']
        assert file_entry.dataset == Dataset.objects.all().last()
        assert file_entry.version.short_name == metadata_correct['version_name']
        assert file_entry.version.pretty_name == metadata_correct['version_pretty_name']
        assert file_entry.version == DatasetVersion.objects.all().last()
        # checking if the proper metadata was retrieved from the file
        assert file_entry.variable == DataVariable.objects.all().last()
        assert file_entry.variable.short_name == 'soil_moisture'
        assert file_entry.time_name == 'time'
        assert file_entry.lat_name == 'lat'
        assert file_entry.lon_name == 'lon'

        # check if the timeseries files were created:
        timeseries_dir = file_entry.get_raw_file_path + '/timeseries'
        assert os.path.exists(timeseries_dir)
        assert len(os.listdir(timeseries_dir)) != 0

        file_entry.delete()
