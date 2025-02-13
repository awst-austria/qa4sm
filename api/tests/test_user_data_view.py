import json
import logging
from api.tests.test_helper import *
from rest_framework.test import APIClient
from django.test.testcases import TransactionTestCase
from django.urls import reverse
from validator.models import UserDatasetFile, DataVariable
from django.conf import settings
import shutil
from pathlib import Path
from api.variable_and_field_names import *
from unittest.mock import patch

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


def _get_headers(metadata):
    return {
        'HTTP_FILEMETADATA': json.dumps(metadata)
    }


def mock_preprocess_file(*args, **kwargs):
    return


class TestUploadUserDataView(TransactionTestCase):
    serialized_rollback = True
    __logger = logging.getLogger(__name__)

    databases = '__all__'
    allow_database_queries = True

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.second_user_data, self.second_test_user = create_alternative_user()

        self.client = APIClient()
        self.client.login(**self.auth_data)
        self.user_data_path = os.path.join(settings.BASE_DIR, 'testdata/user_data')
        self.test_user_data_path = f'{self.user_data_path}/{self.test_user.username}'
        Path(self.test_user_data_path).mkdir(exist_ok=True, parents=True)

        self.netcdf_file_name = 'teststack_c3s_2dcoords_min_attrs.nc'
        self.zipped_netcdf_file_name = 'test_data.zip'
        self.zipped_csv_file_name = 'test_data_csv.zip'
        self.not_netcdf_file_name = 'test_file.txt'

        self.netcdf_file = f'{self.user_data_path}/{self.netcdf_file_name}'
        self.zipped_netcdf = f'{self.user_data_path}/{self.zipped_netcdf_file_name}'
        self.zipped_csv = f'{self.user_data_path}/{self.zipped_csv_file_name}'
        self.not_netcdf_file = f'{self.user_data_path}/{self.not_netcdf_file_name}'

        self.upload_data_url_name = 'Upload user data'
        # self.post_metadata_url_name = 'Post User Data File Metadata'
        self.get_user_data_url_list_name = "Get User Data Files"
        self.delete_data_url_name = 'Delete User Data File'
        self.update_metadata_url_name = 'Update metadata'
        self.get_user_file_by_id_url_name = 'Get user file by ID'
        self.delete_file_only_url_name = "Delete User Data File Only"

        self.metadata_correct = {
            USER_DATA_DATASET_FIELD_NAME: 'test_dataset',
            USER_DATA_DATASET_FIELD_PRETTY_NAME: 'test_dataset_pretty_name',
            USER_DATA_VERSION_FIELD_NAME: 'test_version',
            USER_DATA_VERSION_FIELD_PRETTY_NAME: 'test_version_pretty_name'
        }

        self.partial_metadata_correct = {
            USER_DATA_DATASET_FIELD_NAME: 'test_dataset',
            USER_DATA_DATASET_FIELD_PRETTY_NAME: None,
            USER_DATA_VERSION_FIELD_NAME: 'test_version',
            USER_DATA_VERSION_FIELD_PRETTY_NAME: None
        }

        self.metadata_incorrect = {
            USER_DATA_DATASET_FIELD_NAME: None,
            USER_DATA_DATASET_FIELD_PRETTY_NAME: 'test_dataset',
            USER_DATA_VERSION_FIELD_NAME: None,
            USER_DATA_VERSION_FIELD_PRETTY_NAME: 'test_version'
        }

        self.headers_correct = {
            'HTTP_FILEMETADATA': json.dumps(self.metadata_correct)
        }
        self.headers_partial_correct = {
            'HTTP_FILEMETADATA': json.dumps(self.metadata_correct)
        }

    def _remove_user_datafiles(self, username):
        user_data_path = f'{self.user_data_path}/{username}'
        shutil.rmtree(user_data_path)

    @patch('api.views.upload_user_data_view.preprocess_file', side_effect=mock_preprocess_file)
    def test_file_size_limit(self, mock_preprocess_file):
        headers = _get_headers(self.metadata_correct)

        response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
            {FILE: self.netcdf_file},
            format=FORMAT_MULTIPART,
            **headers)

        file_entry = UserDatasetFile.objects.get(id=response.json()['id'])

        # check the size limit assigned to the user
        assert self.test_user.space_limit == 'basic'
        # check how much space left
        assert self.test_user.space_left == self.test_user.get_space_limit_display() - file_entry.file.size
        # remove the file
        file_entry.delete()

        # change the limit
        self.test_user.space_limit = 'no_data'
        self.test_user.save()

        response = self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                                    {FILE: self.netcdf_file}, format=FORMAT_MULTIPART)

        assert response.json()['error'] == 'File is too big'
        assert response.status_code == 500

        self.test_user.space_limit = 'unlimited'
        self.test_user.save()

        response = self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                                    {FILE: self.netcdf_file}, format=FORMAT_MULTIPART, **headers)

        assert response.status_code == 201

        assert not self.test_user.space_left

        file_entry = UserDatasetFile.objects.get(id=response.json()['id'])
        file_entry.delete()

    @patch('api.views.upload_user_data_view.preprocess_file', side_effect=mock_preprocess_file)
    def test_get_list_of_user_data_files(self, mock_preprocess_file):
        headers = _get_headers(self.metadata_correct)

        # post the same file 3 times, to create 3 different entries
        post_response_1 = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
            {FILE: self.netcdf_file}, format=FORMAT_MULTIPART, **headers)
        assert post_response_1.status_code == 201
        post_response_2 = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
            {FILE: self.netcdf_file}, format=FORMAT_MULTIPART, **headers)
        assert post_response_2.status_code == 201
        post_response_3 = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
            {FILE: self.netcdf_file}, format=FORMAT_MULTIPART, **headers)
        assert post_response_3.status_code == 201

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

    @patch('api.views.upload_user_data_view.preprocess_file', side_effect=mock_preprocess_file)
    def test_get_user_data_file_by_id(self, mock_preprocess_file):
        # post the same file 3 times, to create 3 different entries
        headers = _get_headers(self.metadata_correct)
        post_response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
            {FILE: self.netcdf_file}, format=FORMAT_MULTIPART, **headers)
        assert post_response.status_code == 201

        post_data = post_response.json()
        file_id = post_data.get('id')
        file_entry = UserDatasetFile.objects.get(id=file_id)

        response = self.client.get(reverse(self.get_user_file_by_id_url_name, kwargs={URL_FILE_UUID: file_id}))

        assert response.status_code == 200
        assert post_data.get('file_name') == file_entry.file_name
        assert post_data.get('owner') == file_entry.owner.id
        assert post_data.get('dataset') == file_entry.dataset.id
        assert post_data.get('version') == file_entry.version.id
        assert post_data.get('all_variables') is None
        assert post_data.get('metadata_submitted') is False  # it's submitted after running a preprocessing function

        self.client.logout()
        self.client.login(**self.second_user_data)

        response = self.client.get(reverse(self.get_user_file_by_id_url_name, kwargs={URL_FILE_UUID: file_id}))

        assert response.status_code == 404
        assert response.json().get('detail') == 'Not found.'

        response = self.client.get(
            reverse(self.get_user_file_by_id_url_name, kwargs={URL_FILE_UUID: '00000000-6c36-0000-0000-599e9a3840ca'}))

        assert response.status_code == 404
        assert response.json().get('detail') == 'No UserDatasetFile matches the given query.'

        self.client.logout()
        self.client.login(**self.auth_data)
        file_entry.delete()

    @patch('api.views.upload_user_data_view.preprocess_file', side_effect=mock_preprocess_file)
    def test_delete_user_dataset_and_file(self, mock_preprocess_file):
        # posting a file to be removed

        post_response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
            {FILE: self.netcdf_file},
            format=FORMAT_MULTIPART,
            **_get_headers(self.metadata_correct))

        file_entry_id = post_response.json()['id']
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

        # delete non existing file
        response = self.client.delete(
            reverse(self.delete_data_url_name, kwargs={URL_FILE_UUID: '00000000-6c36-0000-0000-599e9a3840ca'}))

        assert response.status_code == 404
        assert response.json().get('detail') == 'No UserDatasetFile matches the given query.'

        delete_response = self.client.delete(
            reverse(self.delete_data_url_name, kwargs={URL_FILE_UUID: file_entry_id}))

        assert delete_response.status_code == 200
        assert len(Dataset.objects.all()) == 0
        assert len(DatasetVersion.objects.all()) == 0
        assert len(DataVariable.objects.all()) == 0
        assert len(UserDatasetFile.objects.all()) == 0
        assert len(os.listdir(self.test_user_data_path)) == 0

    @patch('api.views.upload_user_data_view.preprocess_file', side_effect=mock_preprocess_file)
    def test_delete_only_user_file(self, mock_preprocess_file):
        # posting a file to be removed

        post_response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
            {FILE: self.netcdf_file},
            format=FORMAT_MULTIPART,
            **_get_headers(self.metadata_correct))

        file_entry_id = post_response.json()['id']
        assert len(Dataset.objects.all()) == 1
        assert len(DatasetVersion.objects.all()) == 1
        assert len(DataVariable.objects.all()) == 1
        assert len(UserDatasetFile.objects.all()) == 1
        assert len(os.listdir(self.test_user_data_path)) == 1

        # checking if another user can remove it:
        self.client.logout()
        self.client.login(**self.second_user_data)
        delete_response = self.client.delete(
            reverse(self.delete_file_only_url_name, kwargs={URL_FILE_UUID: file_entry_id}))

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
            reverse(self.delete_file_only_url_name, kwargs={URL_FILE_UUID: '00000000-6c36-0000-0000-599e9a3840ca'}))

        assert delete_response.status_code == 404
        assert delete_response.json().get('detail') == 'No UserDatasetFile matches the given query.'

        delete_response = self.client.delete(
            reverse(self.delete_file_only_url_name, kwargs={URL_FILE_UUID: file_entry_id}))

        assert delete_response.status_code == 200
        assert len(Dataset.objects.all()) == 1
        assert len(DatasetVersion.objects.all()) == 1
        assert len(DataVariable.objects.all()) == 1
        assert len(UserDatasetFile.objects.all()) == 1
        assert len(os.listdir(self.test_user_data_path)) == 0

        assert Dataset.objects.all()[0].storage_path == ''
        assert not UserDatasetFile.objects.all()[0].file
        assert not UserDatasetFile.objects.all()[0].file_name

    @patch('api.views.upload_user_data_view.preprocess_file', side_effect=mock_preprocess_file)
    def test_upload_user_data_nc_correct(self, mock_preprocess_file):
        response = self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                                    {FILE: self.netcdf_file},
                                    format=FORMAT_MULTIPART,
                                    **_get_headers(self.metadata_correct))

        assert response.status_code == 201

        existing_files = UserDatasetFile.objects.all()

        assert len(existing_files) == 1
        file_entry = existing_files[0]
        file_dir = file_entry.get_raw_file_path

        assert len(os.listdir(self.test_user_data_path)) == 1
        assert os.path.exists(file_dir)

        assert file_entry.dataset.short_name == self.metadata_correct.get(USER_DATA_DATASET_FIELD_NAME)
        assert file_entry.version.short_name == self.metadata_correct.get(USER_DATA_VERSION_FIELD_NAME)
        # this one is none, because it's taken from the file and the file preprocessing is skipped for the purpose of
        # testing
        assert file_entry.variable.short_name == 'none'
        assert file_entry.owner == self.test_user
        file_entry.delete()

        # check if the entry got removed along with the entire file directory
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert not os.path.exists(file_dir)
        assert len(os.listdir(self.test_user_data_path)) == 0

    @patch('api.views.upload_user_data_view.preprocess_file', side_effect=mock_preprocess_file)
    def test_upload_user_data_zip_netcdf_correct(self, mock_preprocess_file):
        response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.zipped_netcdf_file_name}),
            {FILE: self.zipped_netcdf},
            format=FORMAT_MULTIPART,
            **_get_headers(self.metadata_correct))

        assert response.status_code == 201

        existing_files = UserDatasetFile.objects.all()

        assert len(existing_files) == 1
        file_entry = existing_files[0]
        file_dir = file_entry.get_raw_file_path

        assert len(os.listdir(self.test_user_data_path)) == 1
        assert os.path.exists(file_dir)

        file_entry.delete()

        # check if the entry got removed along with the entire file directory
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert not os.path.exists(file_dir)
        assert len(os.listdir(self.test_user_data_path)) == 0

    @patch('api.views.upload_user_data_view.preprocess_file', side_effect=mock_preprocess_file)
    def test_upload_user_data_zip_csv_correct(self, mock_preprocess_file):
        response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.zipped_csv_file_name}),
            {FILE: self.zipped_csv},
            format=FORMAT_MULTIPART,
            **_get_headers(self.metadata_correct)
        )

        assert response.status_code == 201

        existing_files = UserDatasetFile.objects.all()

        assert len(existing_files) == 1
        file_entry = existing_files[0]
        file_dir = file_entry.get_raw_file_path

        assert len(os.listdir(self.test_user_data_path)) == 1
        assert os.path.exists(file_dir)

        file_entry.delete()

        # check if the entry got removed along with the entire file directory
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert not os.path.exists(file_dir)
        assert len(os.listdir(self.test_user_data_path)) == 0

    def test_upload_user_data_not_porper_extension(self):
        file_to_upload = _create_test_file(self.not_netcdf_file)
        response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.not_netcdf_file_name}),
            {FILE: file_to_upload},
            format=FORMAT_MULTIPART,
            **_get_headers(self.metadata_correct))
        # assert False
        assert response.status_code == 500

        # checking if nothing got to the db and to the data path
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert len(os.listdir(self.test_user_data_path)) == 0

    @patch('api.views.upload_user_data_view.preprocess_file', side_effect=mock_preprocess_file)
    def test_upload_user_data_with_wrong_name(self, mock_preprocess_file):
        file_to_upload = _create_test_file(self.not_netcdf_file)
        response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: 'wrong_name'}),
            {FILE: file_to_upload},
            format=FORMAT_MULTIPART,
            **_get_headers(self.metadata_correct)
        )
        # assert False
        assert response.status_code == 500

        # checking if nothing got to the db and to the data path
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0
        assert len(os.listdir(self.test_user_data_path)) == 0

    def test_post_incorrect_metadata_form(self):
        # I am posting the file to create the proper dataset entry, I don't need to copy it, as it won't be processed
        response = self.client.post(reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
                                    {FILE: self.netcdf_file},
                                    format=FORMAT_MULTIPART,
                                    **_get_headers(self.metadata_incorrect))
        assert response.status_code == 500

        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 0

    @patch('api.views.upload_user_data_view.preprocess_file', side_effect=mock_preprocess_file)
    def test_update_metadata(self, mock_preprocess_file):
        file_post_response = self.client.post(
            reverse(self.upload_data_url_name, kwargs={URL_FILENAME: self.netcdf_file_name}),
            {FILE: self.netcdf_file},
            format=FORMAT_MULTIPART,
            **_get_headers(self.metadata_correct))

        assert file_post_response.status_code == 201

        file_id = file_post_response.json()['id']
        file_entry = UserDatasetFile.objects.get(pk=file_id)
        file_entry.all_variables = [{"name": "soil_moisture", "units": "%", "long_name": "Soil Moisture"},
                                    {"name": "ssm_noise", "units": "%", "long_name": "Surface Soil Moisture Noise"}]
        file_entry.save()

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
