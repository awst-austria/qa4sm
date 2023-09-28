import logging
import shutil
from os import path

import pytest
from django.test.utils import override_settings
from django.urls import reverse

from django.test import TestCase
from rest_framework.test import APIClient

from api.tests.test_helper import *
from validator.forms import PublishingForm
from validator.models import ValidationRun
from dateutil import parser

from validator.validation import mkdir_if_not_exists, set_outfile

User = get_user_model()
from unittest.mock import patch


def mock_get_doi(*args, **kwargs):
    return


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestModifyValidationView(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']
    __logger = logging.getLogger(__name__)

    def setUp(self):
        # creating the main user to run a validation
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)
        # creating an alternative user for some tests
        self.alt_data, self.alt_test_user = create_alternative_user()
        # start a new validation, which will be used by some tests below
        self.run = create_default_validation_without_running(self.test_user)
        self.run.save()
        self.run_id = self.run.id
        self.wrong_id = 'f0000000-a000-b000-c000-d00000000000'

        self.run_2 = create_default_validation_without_running(self.alt_test_user, tcol=True)
        self.run_2.save()

    def test_change_name(self):
        change_name_url = reverse('Change name', kwargs={'result_uuid': self.run_id})
        # everything ok
        body = {'save_name': True, 'new_name': 'validation_new_name'}
        response = self.client.patch(change_name_url, body, format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 200
        assert new_run.name_tag == 'validation_new_name'

        # wrong id
        body = {'save_name': True, 'new_name': 'validation_new_name'}
        response = self.client.patch(reverse('Change name', kwargs={'result_uuid': self.wrong_id}), body, format='json')
        assert response.status_code == 404
        assert new_run.name_tag == 'validation_new_name'

        # save_name == False
        body = {'save_name': False, 'new_name': 'wrong_name'}
        response = self.client.patch(change_name_url, body, format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 400  # status 400
        assert new_run.name_tag == 'validation_new_name'  # name has not been changed

        # "published" validation
        new_run.doi = '1000101010101010'
        new_run.is_archived = True
        new_run.save()

        body = {'save_name': True, 'new_name': 'some_other_name'}
        response = self.client.patch(change_name_url, body, format='json')

        assert response.status_code == 405  # status 405
        assert new_run.name_tag == 'validation_new_name'  # name has not been changed

        # getting back to former settings
        new_run.doi = ''
        new_run.is_archived = False

        # log out the owner and log in other user
        self.client.login(**self.alt_data)
        body = {'save_name': True, 'new_name': 'some_other_name'}
        response = self.client.patch(change_name_url, body, format='json')

        assert response.status_code == 403  # status 403
        assert new_run.name_tag == 'validation_new_name'  # name has not been changed

    def test_archive_result(self):
        archive_url = reverse('Archive results', kwargs={'result_uuid': self.run_id})

        # everything ok, I want to archive ========================================================================
        body = {'archive': True}
        response = self.client.patch(archive_url, body, format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 200
        assert new_run.is_archived is True

        # everything still ok, now I want to un-archive ==========================================================
        body = {'archive': False}
        response = self.client.patch(archive_url, body, format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 200
        assert new_run.is_archived is False

        # wrong id =====================================================================
        body = {'archive': False}
        response = self.client.patch(reverse('Archive results', kwargs={'result_uuid': self.wrong_id}), body,
                                     format='json')
        assert response.status_code == 404
        assert new_run.is_archived is False

        # not valid parameter ==========================================================
        body = {'archive': 'some_not_valid_parameter'}
        response = self.client.patch(archive_url, body, format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 400
        assert new_run.is_archived is False  # nothing has changed

        # not valid method ==========================================================
        body = {'archive': True}
        response = self.client.get(archive_url, body, format='json')  # should be patch

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 405
        assert new_run.is_archived is False  # nothing has changed

        # you can't modify a published validation ==========================================================
        new_run.doi = '1010101010101'
        new_run.save()

        body = {'archive': True}
        response = self.client.patch(archive_url, body, format='json')
        assert response.status_code == 405

        new_run.doi = ''
        new_run.save()

        # log out and log in another user to check if only owners should be able to change validations ===============
        self.client.login(**self.alt_data)

        body = {'archive': True}
        response = self.client.patch(archive_url, body, format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 403
        assert new_run.is_archived is False  # nothing has changed

    def test_extend_result(self):
        extend_result_url = reverse('Extend results', kwargs={'result_uuid': self.run_id})

        # everything ok ==============================================================
        body = {'extend': True}
        response = self.client.patch(extend_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)
        new_expiry_date = parser.parse(response.content)

        assert response.status_code == 200
        assert new_expiry_date is not None
        assert new_run.expiry_date == new_expiry_date

        # invalid expiry extension ==================================================
        body = {'extend': False}
        response = self.client.patch(extend_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)

        assert response.status_code == 400
        assert new_run.expiry_date == new_expiry_date  # nothing has changed

        # wrong id ===================================================================
        body = {'extend': True}
        response = self.client.patch(reverse('Extend results', kwargs={'result_uuid': self.wrong_id}), body,
                                     format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)

        assert response.status_code == 404
        assert new_run.expiry_date == new_expiry_date  # nothing has changed

        # published validation =======================================================
        new_run.doi = '1010101019110'
        new_run.save()

        body = {'extend': True}
        response = self.client.patch(extend_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 405
        assert new_run.expiry_date == new_expiry_date  # nothing has changed

        new_run.doi = ''
        new_run.save()

        # wrong user =================================================================
        self.client.login(**self.alt_data)  # log in as another one

        body = {'extend': True}
        response = self.client.patch(extend_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 403
        assert new_run.expiry_date == new_expiry_date  # nothing has changed

    @pytest.mark.skipif(not 'DOI_ACCESS_TOKEN_ENV' in os.environ, reason="No access token set in global variables")
    @override_settings(DOI_REGISTRATION_URL="https://sandbox.zenodo.org/api/deposit/depositions")
    @patch('api.views.modify_validation_view.get_doi_process', side_effect=mock_get_doi)
    def test_publish_result(self, mock_get_doi):
        infile = 'testdata/output_data/c3s_era5land.nc'

        publish_result_url = reverse('Publish result', kwargs={'result_uuid': self.run_id})
        # use the publishing form to convert the validation metadata to a dict
        publishing_form = PublishingForm()._formdata_from_validation(self.run)

        # shouldn't work because of incorrect parameter 'publish' ========================================
        body = {'publish': False, 'publishing_form': publishing_form}
        response = self.client.patch(publish_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)

        assert response.status_code == 400
        assert new_run.is_unpublished

        # wrong id ==============================================================
        body = {'publish': True, 'publishing_form': publishing_form}
        response = self.client.patch(reverse('Publish result', kwargs={'result_uuid': self.wrong_id}), body,
                                     format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)

        assert response.status_code == 404
        assert new_run.is_unpublished

        # wrong user =============================================================
        self.client.login(**self.alt_data)

        body = {'publish': True, 'publishing_form': publishing_form}
        response = self.client.patch(publish_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)

        assert response.status_code == 403
        assert new_run.is_unpublished

        # log in the author again
        self.client.login(**self.auth_data)

        # shouldn't work because input metadata is not valid =================================================
        original_orcid = publishing_form['orcid']
        original_keywords = publishing_form['keywords']

        # wrong orcid
        publishing_form['orcid'] = 'this is no orcid'
        body = {'publish': True, 'publishing_form': publishing_form}
        response = self.client.patch(publish_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)

        assert response.status_code == 400
        assert new_run.is_unpublished

        # good orcid, wrong keywords
        publishing_form['orcid'] = original_orcid
        publishing_form['keywords'] = publishing_form['keywords'].replace('qa4sm', '')

        body = {'publish': True, 'publishing_form': publishing_form}
        response = self.client.patch(publish_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)

        assert response.status_code == 400
        assert new_run.is_unpublished

        # good keywords, missing file
        publishing_form['keywords'] = original_keywords

        # remove file path from validation
        self.run.output_file = None
        self.run.save()

        body = {'publish': True, 'publishing_form': publishing_form}
        response = self.client.patch(publish_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run.id)

        assert response.status_code == 405
        assert new_run.is_unpublished
        assert new_run.output_file == ''

        # set valid output file for validation
        run_dir = path.join(OUTPUT_FOLDER, str(self.run_id))
        mkdir_if_not_exists(run_dir)
        shutil.copy(infile, path.join(run_dir, 'results.nc'))
        set_outfile(self.run, run_dir)
        self.run.save()
        new_run = ValidationRun.objects.get(pk=self.run_id)

        assert new_run.output_file != ''

        # simulate that publishing is already in progress
        self.run.publishing_in_progress = True
        self.run.save()

        body = {'publish': True, 'publishing_form': publishing_form}
        response = self.client.patch(publish_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run.id)

        assert response.status_code == 405
        assert new_run.is_unpublished

        # remove in progress flag
        self.run.publishing_in_progress = False
        self.run.save()

        # check if it works if the validation has been already published
        self.run.doi = '191012912039'
        self.run.save()

        body = {'publish': True, 'publishing_form': publishing_form}
        response = self.client.patch(publish_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run.id)

        assert response.status_code == 405
        assert not new_run.is_unpublished

        # 'un-publish' validation
        self.run.doi = ''
        self.run.save()

        # now it should work
        body = {'publish': True, 'publishing_form': publishing_form}
        response = self.client.patch(publish_result_url, body, format='json')
        new_run = ValidationRun.objects.get(pk=self.run.id)

        assert response.status_code == 200

    def test_add_validation(self):
        add_validation_url = reverse('Add validation', kwargs={'result_uuid': self.run_id})

        # everything ok =========================================================================
        body = {'add_validation': True}
        response = self.client.post(add_validation_url, body, format='json')

        assert response.status_code == 200
        assert len(self.test_user.copied_runs.all()) == 1

        # wrong method =========================================================================
        body = {'add_validation': True}
        response = self.client.patch(add_validation_url, body, format='json')

        assert response.status_code == 405
        assert len(self.test_user.copied_runs.all()) == 1

        # wrong id =========================================================================
        body = {'add_validation': True}
        response = self.client.post(reverse('Add validation', kwargs={'result_uuid': self.wrong_id}), body,
                                    format='json')

        assert response.status_code == 404
        assert len(self.test_user.copied_runs.all()) == 1

        # wrong parameter =========================================================================
        body = {'add_validation': False}
        response = self.client.post(add_validation_url, body, format='json')

        assert response.status_code == 400
        assert len(self.test_user.copied_runs.all()) == 1

        # trying to add it the second time, it doesn't raise an error but does not add it second time ==============
        body = {'add_validation': True}
        response = self.client.post(add_validation_url, body, format='json')

        assert response.status_code == 200
        assert len(self.test_user.copied_runs.all()) == 1  # still one, the validation is already there

        # trying to add as another user - should be possible ==============
        self.client.login(**self.alt_data)

        body = {'add_validation': True}
        response = self.client.post(add_validation_url, body, format='json')

        assert response.status_code == 200
        assert len(self.test_user.copied_runs.all()) == 1  # should be one

    def test_remove_validation(self):
        add_validation_url = reverse('Add validation', kwargs={'result_uuid': self.run_id})
        remove_validation_url = reverse('Remove validation', kwargs={'result_uuid': self.run_id})

        # first a validation has to be added
        body = {'add_validation': True}
        self.client.post(add_validation_url, body, format='json')

        # wrong method =========================================================================
        body = {'remove_validation': True}
        response = self.client.patch(remove_validation_url, body, format='json')

        assert response.status_code == 405
        assert len(self.test_user.copied_runs.all()) == 1

        # wrong id =========================================================================
        body = {'remove_validation': True}
        response = self.client.post(reverse('Remove validation', kwargs={'result_uuid': self.wrong_id}), body,
                                    format='json')

        assert response.status_code == 404
        assert len(self.test_user.copied_runs.all()) == 1

        # wrong parameter =========================================================================
        body = {'remove_validation': False}
        response = self.client.post(remove_validation_url, body, format='json')

        assert response.status_code == 400
        assert len(self.test_user.copied_runs.all()) == 1

        # everything ok =========================================================================
        body = {'remove_validation': True}
        response = self.client.post(remove_validation_url, body, format='json')

        assert response.status_code == 200
        assert len(self.test_user.copied_runs.all()) == 0

        # trying to remove it the second time, it doesn't raise an error ============================
        body = {'remove_validation': True}
        response = self.client.post(remove_validation_url, body, format='json')

        assert response.status_code == 200

        # another user
        self.client.login(**self.alt_data)

        body = {'add_validation': True}
        self.client.post(add_validation_url, body, format='json')

        body = {'remove_validation': True}
        response = self.client.post(remove_validation_url, body, format='json')

        assert response.status_code == 200
        assert len(self.test_user.copied_runs.all()) == 0

    def test_delete_result(self):
        delete_validation_url = reverse('Delete validation', kwargs={'result_uuid': self.run_id})

        # published validation - can not be removed
        self.run.doi = '19282843'
        self.run.save()

        response = self.client.delete(delete_validation_url)

        assert response.status_code == 405
        assert len(ValidationRun.objects.filter(pk=self.run_id)) == 1  # validation still there

        self.run.doi = ''
        self.run.save()

        # someone else's validation
        self.client.login(**self.alt_data)
        response = self.client.delete(delete_validation_url)

        assert response.status_code == 403
        assert len(ValidationRun.objects.filter(pk=self.run_id)) == 1  # validation still there

        # non-existing validation
        self.client.login(**self.auth_data)  # getting back to the right user
        response = self.client.delete(reverse('Delete validation', kwargs={'result_uuid': self.wrong_id}))

        assert response.status_code == 404
        assert len(ValidationRun.objects.filter(pk=self.run_id)) == 1  # validation still there

        # wrong method
        response = self.client.post(delete_validation_url)

        assert response.status_code == 405
        assert len(ValidationRun.objects.filter(pk=self.run_id)) == 1  # validation still there

        # finally should work
        response = self.client.delete(delete_validation_url)

        assert response.status_code == 200
        assert len(ValidationRun.objects.filter(pk=self.run_id)) == 0  # not there anymore

    def test_delete_multiple_results(self):
        create_default_validation_without_running(self.test_user)
        create_default_validation_without_running(self.test_user)
        all_validations = ValidationRun.objects.all()

        assert len(ValidationRun.objects.all()) == 4

        self.run.doi = '19282843'
        self.run.save()

        delete_validation_url = reverse('Delete Multiple Validations') + '?'
        val_ids = [str(validation.id) for validation in all_validations]
        for id in val_ids:
            delete_validation_url += f'id={id}&'
        delete_validation_url = delete_validation_url.rstrip('&')

        response = self.client.delete(delete_validation_url)

        assert response.status_code == 200
        assert len(ValidationRun.objects.all()) == 2  # 2 left, one belonging to othe user, second one published.

    def test_get_publishing_form(self):
        get_publishing_form_url = reverse('Get publishing form')

        response = self.client.get(get_publishing_form_url + f'?id={self.run_id}')
        assert response.status_code == 200
        assert 'qa4sm' in response.json()['keywords']
        assert response.json()['name'] == self.test_user.last_name + ', ' + self.test_user.first_name

        # wrong validation id
        response = self.client.get(get_publishing_form_url + f'?id={self.wrong_id}')
        assert response.status_code == 404

        # logged out user
        self.client.logout()
        response = self.client.get(get_publishing_form_url + f'?id={self.run_id}')
        assert response.status_code == 403

        self.client.login(**self.alt_data)
        response = self.client.get(get_publishing_form_url + f'?id={self.run_id}')
        assert response.status_code == 403
        assert response.json()['message'] == 'Validation does not belong to the current user'

    def test_copy_validation_results(self):
        copy_validation_url = reverse('Copy validation results')

        # everything is ok
        response = self.client.get(copy_validation_url + f'?validation_id={self.run_2.id}')
        assert response.status_code == 200
        assert response.json()['run_id'] != self.run_2.id  # copied validation has different id
        assert ValidationRun.objects.get(pk=response.json()['run_id']).user == self.test_user
        assert self.run_2.user == self.alt_test_user  # and the user of the validation being copied has not changed

        # non existing validation
        response = self.client.get(copy_validation_url + f'?validation_id={self.wrong_id}')
        assert response.status_code == 404

        # I can copy also my own validation - not possible from the UI though
        response = self.client.get(copy_validation_url + f'?validation_id={self.run.id}')
        assert response.status_code == 200
        assert response.json()['run_id'] != self.run.id  # copied validation has different id
        assert ValidationRun.objects.get(pk=response.json()['run_id']).user == self.test_user

        # not possible to copy if a user is not logged in
        self.client.logout()
        response = self.client.get(copy_validation_url + f'?validation_id={self.run_2.id}')
        assert response.status_code == 403
