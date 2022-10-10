import logging
from django.test import TestCase
from django.utils import timezone

from api.tests.test_helper import *
from rest_framework.test import APIClient, APIRequestFactory, APITestCase
from django.urls import reverse
from validator.models import UserDatasetFile, DatasetVersion, DataVariable, Dataset
from django.conf import settings

class TestUploadUserDataView(APITestCase):
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.second_user_data, self.second_test_user = create_alternative_user()

        self.client = APIClient()
        self.client.login(**self.auth_data)

        self.file_name = 'teststack_c3s_2dcoords_min_attrs.nc'
        self.user_data_path = os.path.join(settings.BASE_DIR, 'testdata/user_data')
        self.file = f'{self.user_data_path}/{self.file_name}'
        # self.file = f'/testdata/user_data/{self.file_name}'
        self.upload_data_url_name = 'Upload user data'
        self.post_metadata_url_name = 'Post User Data File Metadata'

    def test_upload_user_data(self):
        response = self.client.post(reverse(self.upload_data_url_name, kwargs={'filename': self.file_name}),
                                    {'file': self.file}, format='multipart')

        assert response.status_code == 200

        existing_files = UserDatasetFile.objects.all()

        assert len(existing_files) == 1
        file_entry = existing_files[0]
        assert file_entry.dataset is None  # metadata hasn't been posted yet
        assert file_entry.version is None  # metadata hasn't been posted yet
        assert file_entry.variable is None  # metadata hasn't been posted yet
        assert file_entry.lon_name is None  # metadata hasn't been posted yet
        assert file_entry.lat_name is None  # metadata hasn't been posted yet
        assert file_entry.time_name is None  # metadata hasn't been posted yet
        assert file_entry.owner == self.test_user
        file_entry.delete()

    def test_post_user_file_metadata_and_preprocess_file(self):
        # new file entry -> an existing proper file
        file_entry = UserDatasetFile(file_name=self.file_name, owner=self.test_user, upload_date=timezone.now())
        file_entry.file.name = self.file
        file_entry.save()

        # checking if the file entry got saved
        existing_files = UserDatasetFile.objects.all()
        assert len(existing_files) == 1

        metadata_correct = {
            'dataset_name': 'test_dataset',
            'dataset_pretty_name': 'test_dataset_pretty_name',
            'version_name': 'test_version',
            'version_pretty_name': 'test_version_pretty_name'
        }

        response_metadata = self.client.post(reverse(self.post_metadata_url_name, kwargs={'file_uuid': file_entry.id}),
                                             metadata_correct, format='json')

        file_entry = UserDatasetFile.objects.get(id=file_entry.id)
        assert response_metadata.status_code == 200
        assert file_entry.dataset.short_name == metadata_correct['dataset_name']
        assert file_entry.dataset.pretty_name == metadata_correct['dataset_pretty_name']
        assert file_entry.version.short_name == metadata_correct['version_name']
        assert file_entry.version.pretty_name == metadata_correct['version_pretty_name']
        assert file_entry.variable == DataVariable.objects.all().last()
        assert file_entry.variable.short_name == 'soil_moisture'
        assert file_entry.time_name == 'time'
        assert file_entry.lat_name == 'lat'
        assert file_entry.lon_name == 'lon'

        file_entry.delete()
        # assert False
