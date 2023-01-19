import logging
from api.tests.test_helper import *
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from validator.models import UserDatasetFile, DataVariable
from django.conf import settings
import shutil
from pathlib import Path
from api.variable_and_field_names import *

FILE = 'file'
FORMAT_MULTIPART = 'multipart'
# todo: test for a file with no variables - file with no variables needed
def _create_test_file(path):
    test_file = open(path, 'w')
    test_file.write('some test content of a not netcdf file\n')
    test_file.close()
    test_file = open(path, 'rb')
    return test_file


def _clean_up_data(file_entry):
    datafile = file_entry.file.path
    outdir = os.path.dirname(datafile)
    assert os.path.isfile(datafile)
    file_entry.delete()
    assert not os.path.exists(outdir)


def _update_file_entry(file_entry):
    new_dataset = Dataset()
    new_dataset.save()
    new_version = DatasetVersion()
    new_version.save()
    new_variable = DataVariable()
    new_variable.save()

    file_entry.dataset = new_dataset
    file_entry.version = new_version
    file_entry.variable = new_variable
    file_entry.all_variables = [
        {'name': 'soil_moisture', 'long_name': 'Soil Moisture'},
        {'name': 'none', 'long_name': 'Some weird variable'}
    ]
    file_entry.save()


class TestUploadUserDataView(APITestCase):
    __logger = logging.getLogger(__name__)

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
        self.get_user_data_url_list_name = "Get User Data Files"
        self.delete_data_url_name = 'Delete User Data File'
        self.update_metadata_url_name = 'Update metadata'

    def _remove_user_datafiles(self, username):
        user_data_path = f'{self.user_data_path}/{username}'
        shutil.rmtree(user_data_path)

    def test_get_list_of_user_data_files(self):
        # post the same file 3 times, to create 3 different entries
        self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                         {FILE: self.netcdf_file}, format=FORMAT_MULTIPART)
        self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                         {FILE: self.netcdf_file}, format=FORMAT_MULTIPART)
        self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                         {FILE: self.netcdf_file}, format=FORMAT_MULTIPART)

        response = self.client.get(reverse(self.get_user_data_url_list_name))
        existing_files = response.json()

        assert response.status_code == 200
        assert len(existing_files) == 3

        # log out and log in as another user
        self.client.logout()
        self.client.login(**self.second_user_data)

        # there should be no files available
        response = self.client.get(reverse(self.get_user_data_url_list_name))
        existing_files = response.json()
        assert response.status_code == 200
        assert len(existing_files) == 0

        self.client.logout()
        self.client.login(**self.auth_data)
        assert len(os.listdir(self.test_user_data_path)) == 3
        self._remove_user_datafiles(self.test_user)
        assert not os.path.exists(self.test_user_data_path)

        # there are no files, so there will be an error returned;
        response = self.client.get(reverse(self.get_user_data_url_list_name))
        assert response.status_code == 500

        # cleaning
        for entry in UserDatasetFile.objects.all():
            entry.delete()

        assert len(UserDatasetFile.objects.all()) == 0

    def test_delete_user_dataset_and_file(self):
        # posting a file to be removed
        post_response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
            {FILE: self.netcdf_file}, format=FORMAT_MULTIPART)
        file_entry_id = post_response.json()['id']
        file_entry = UserDatasetFile.objects.get(pk=file_entry_id)

        _update_file_entry(file_entry)

        assert len(Dataset.objects.all()) == 1
        assert len(DatasetVersion.objects.all()) == 1
        assert len(DataVariable.objects.all()) == 1
        assert len(UserDatasetFile.objects.all()) == 1
        assert len(os.listdir(self.test_user_data_path)) == 1

        # checking if another user can remove it:
        self.client.logout()
        self.client.login(**self.second_user_data)
        delete_response = self.client.delete(
            reverse(self.delete_data_url_name, kwargs={URL_FILE_UUID: file_entry_id}))

        assert delete_response.status_code == 403
        # nothing happened, as the user has no credentials
        assert len(Dataset.objects.all()) == 1
        assert len(DatasetVersion.objects.all()) == 1
        assert len(DataVariable.objects.all()) == 1
        assert len(UserDatasetFile.objects.all()) == 1
        assert len(os.listdir(self.test_user_data_path)) == 1

        # loging in as the proper user:
        self.client.login(**self.auth_data)
        delete_response = self.client.delete(
            reverse(self.delete_data_url_name, kwargs={URL_FILE_UUID: file_entry_id}))

        assert delete_response.status_code == 200
        assert len(Dataset.objects.all()) == 0
        assert len(DatasetVersion.objects.all()) == 0
        assert len(DataVariable.objects.all()) == 0
        assert len(UserDatasetFile.objects.all()) == 0
        assert len(os.listdir(self.test_user_data_path)) == 0

    def test_upload_user_data_correct(self):
        response = self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                                    {FILE: self.netcdf_file}, format=FORMAT_MULTIPART)

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
        assert file_entry.owner == self.test_user
        file_entry.delete()

        # check if the entry got removed along with the entire file directory
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert not os.path.exists(file_dir)
        assert len(os.listdir(self.test_user_data_path)) == 0

    def test_upload_user_data_not_netcdf(self):
        file_to_upload = _create_test_file(self.not_netcdf_file)
        response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.not_netcdf_file_name}),
            {FILE: file_to_upload}, format=FORMAT_MULTIPART)
        # assert False
        assert response.status_code == 500

        # checking if nothing got to the db and to the data path
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert len(os.listdir(self.test_user_data_path)) == 0

    def test_upload_user_data_with_wrong_name(self):
        file_to_upload = _create_test_file(self.not_netcdf_file)
        response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: 'wrong_name'}),
            {FILE: file_to_upload}, format=FORMAT_MULTIPART)
        # assert False
        assert response.status_code == 500

        # checking if nothing got to the db and to the data path
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert len(os.listdir(self.test_user_data_path)) == 0

    def test_post_user_file_metadata_and_preprocess_file_correct(self):
        # I am posting the file to create the proper dataset entry
        response = self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                                    {FILE: self.netcdf_file}, format=FORMAT_MULTIPART)
        assert response.status_code == 200

        # checking if the file entry got saved
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 1

        file_entry = existing_files[0]
        # I need to replace the posted file with the original one, because the api post method somehow corrupts netCDFs
        # which is not the problem when I post them via angular and I don't want to deal with it right now.
        shutil.copy2(self.netcdf_file, file_entry.file.path)

        metadata_correct = {
            USER_DATA_DATASET_FIELD_NAME: 'test_dataset',
            USER_DATA_DATASET_FIELD_PRETTY_NAME: 'test_dataset_pretty_name',
            USER_DATA_VERSION_FIELD_NAME: 'test_version',
            USER_DATA_VERSION_FIELD_PRETTY_NAME: 'test_version_pretty_name'
        }
        # posting metadata as those from the metadata form and checking if it has been done
        response_metadata = self.client.post(
            reverse(self.post_metadata_url_name, kwargs={URL_FILE_UUID: file_entry.id}),
            metadata_correct, format='json')
        assert response_metadata.status_code == 200

        # re-querying file entry
        file_entry = UserDatasetFile.objects.get(id=response.json()['id'])
        # checking if the posted metadata is proper
        assert file_entry.dataset.short_name == metadata_correct[USER_DATA_DATASET_FIELD_NAME]
        assert file_entry.dataset.pretty_name == metadata_correct[USER_DATA_DATASET_FIELD_PRETTY_NAME]
        assert file_entry.dataset == Dataset.objects.all().last()
        assert file_entry.version.short_name == metadata_correct[USER_DATA_VERSION_FIELD_NAME]
        assert file_entry.version.pretty_name == metadata_correct[USER_DATA_VERSION_FIELD_PRETTY_NAME]
        assert file_entry.version == DatasetVersion.objects.all().last()

        # checking if the proper metadata was retrieved from the file
        assert file_entry.variable == DataVariable.objects.all().last()
        # the values below are defined in the test file, so if we change the test file we may have to update them
        assert file_entry.variable.short_name == 'soil_moisture'

        # check if the timeseries files were created:
        timeseries_dir = file_entry.get_raw_file_path + '/timeseries'
        assert os.path.exists(timeseries_dir)
        assert len(os.listdir(timeseries_dir)) != 0

        file_entry.delete()
        assert len(UserDatasetFile.objects.all()) == 0

    def test_post_incorrect_metadata_form(self):
        # I am posting the file to create the proper dataset entry, I don't need to copy it, as it won't be processed
        response = self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                                    {FILE: self.netcdf_file}, format=FORMAT_MULTIPART)
        assert response.status_code == 200

        # checking if the file entry got saved
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 1

        file_entry = existing_files[0]
        metadata_correct = {
            USER_DATA_DATASET_FIELD_NAME: None,
            USER_DATA_DATASET_FIELD_PRETTY_NAME: 'test_dataset_pretty_name',
            USER_DATA_VERSION_FIELD_NAME: None,
            USER_DATA_VERSION_FIELD_PRETTY_NAME: 'test_version_pretty_name'
        }
        # posting metadata as those from the metadata form and checking if it has been done
        response_metadata = self.client.post(
            reverse(self.post_metadata_url_name, kwargs={URL_FILE_UUID: file_entry.id}),
            metadata_correct, format='json')
        assert response_metadata.status_code == 500
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0

    def test_preprocess_corrupted_file(self):
        """ For some reason, when a netCDF is posted with django rest client it gets corrupted, so with this test I want
        to check two things: 1. if the corrupted file exception is handled, 2. if at some point they change something
        and the file won't be spoiled anymore. If this test starts failing at some point that might be the indicator"""

        # I am posting the file to create the proper dataset entry
        response = self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                                    {FILE: self.netcdf_file}, format=FORMAT_MULTIPART)
        assert response.status_code == 200

        # checking if the file entry got saved
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 1

        file_entry = existing_files[0]
        # pretty names are not required
        metadata_correct = {
            USER_DATA_DATASET_FIELD_NAME: 'test_dataset',
            USER_DATA_DATASET_FIELD_PRETTY_NAME: None,
            USER_DATA_VERSION_FIELD_NAME: 'test_version',
            USER_DATA_VERSION_FIELD_PRETTY_NAME: None
        }
        # posting metadata as those from the metadata form and checking if it has been done
        response_metadata = self.client.post(
            reverse(self.post_metadata_url_name, kwargs={URL_FILE_UUID: file_entry.id}),
            metadata_correct, format='json')
        assert response_metadata.status_code == 500
        assert response_metadata.json()['error'] == 'Wrong file format or file is corrupted'
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0

    def test_update_metadata(self):
        file_post_response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
            {FILE: self.netcdf_file}, format=FORMAT_MULTIPART)

        assert file_post_response.status_code == 200

        file_id = file_post_response.json()['id']
        file_entry = UserDatasetFile.objects.get(pk=file_id)
        _update_file_entry(file_entry)

        # update variable name
        variable_new_name = 'soil_moisture'
        response = self.client.put(reverse(self.update_metadata_url_name, kwargs={URL_FILE_UUID: file_id}),
                                   {USER_DATA_FIELD_NAME: USER_DATA_VARIABLE_FIELD_NAME,
                                    USER_DATA_FIELD_VALUE: variable_new_name})
        assert response.status_code == 200
        # check if the variable name got updated:
        variable = DataVariable.objects.get(pk=file_entry.variable_id)
        assert variable.short_name == variable_new_name
        assert variable.pretty_name == 'Soil Moisture'

        # update dataset name
        datset_new_name = 'test_dataset'
        response = self.client.put(reverse(self.update_metadata_url_name, kwargs={URL_FILE_UUID: file_id}),
                                   {USER_DATA_FIELD_NAME: USER_DATA_DATASET_FIELD_NAME,
                                    USER_DATA_FIELD_VALUE: datset_new_name})
        assert response.status_code == 200
        # check if the variable name got updated:
        dataset = Dataset.objects.get(pk=file_entry.dataset_id)
        assert dataset.pretty_name == datset_new_name

        # update version name
        version_new_name = 'test_version'
        response = self.client.put(reverse(self.update_metadata_url_name, kwargs={URL_FILE_UUID: file_id}),
                                   {USER_DATA_FIELD_NAME: USER_DATA_VERSION_FIELD_NAME,
                                    USER_DATA_FIELD_VALUE: version_new_name})
        assert response.status_code == 200
        # check if the variable name got updated:
        version = DatasetVersion.objects.get(pk=file_entry.version_id)
        assert version.pretty_name == version_new_name

        file_entry.delete()
