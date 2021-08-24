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

from validator.validation import mkdir_if_not_exists, set_outfile

User = get_user_model()


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestModifyValidationView(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters']
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
        # val.run_validation(self.run_id)

    def test_stop_validation(self):
        # start a new validation (tcol is run here, because a default one would finish before I cancel it :) )
        run = default_parameterized_validation_to_be_run(self.test_user, tcol=True)
        run.save()
        run_id = run.id
        val.run_validation(run_id)
        new_run = ValidationRun.objects.get(pk=run_id)

        # let it run a little bit
        time.sleep(2)
        # the validation has just started so the progress must be below 100
        assert new_run.progress < 100

        # now let's try out cancelling the validation
        response = self.client.delete(reverse('Stop validation', kwargs={'result_uuid': new_run.id}))
        assert response.status_code == 200

        # let's try canceling non existing validation
        response = self.client.delete(reverse('Stop validation', kwargs={'result_uuid': 'f0000000-a000-b000-c000-d00000000000'}))
        assert response.status_code == 404

        # let's try to submit wrong method
        response = self.client.get(reverse('Stop validation', kwargs={'result_uuid': new_run.id}))
        assert response.status_code == 405

        # log out and check the access
        self.client.logout()
        response = self.client.delete(reverse('Stop validation', kwargs={'result_uuid': new_run.id}))
        assert response.status_code == 403
        #
        # log in as another user and check the access
        self.client.login(**self.alt_data)
        response = self.client.delete(reverse('Stop validation', kwargs={'result_uuid': new_run.id}))
        assert response.status_code == 403

        # give it some time
        time.sleep(2)
        # the progress should be -1, but it takes some time for a validation to settle down so setting -1 here would
        # require some time, but we can check that it's not bigger than 0 so there was no progress
        assert new_run.progress <= 0
        delete_run(new_run)

    def test_change_name(self):
        change_name_url = reverse('Change name', kwargs={'result_uuid': self.run_id})
        # everything ok
        body = {'save_name': True, 'new_name': 'validation_new_name'}
        response = self.client.patch(change_name_url, body,  format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 200
        assert new_run.name_tag == 'validation_new_name'

        # wrong id
        body = {'save_name': True, 'new_name': 'validation_new_name'}
        response = self.client.patch(reverse('Change name', kwargs={'result_uuid': self.wrong_id}), body,  format='json')
        assert response.status_code == 404
        assert new_run.name_tag == 'validation_new_name'

        # save_name == False
        body = {'save_name': False, 'new_name': 'wrong_name'}
        response = self.client.patch(change_name_url, body,  format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 400  # status 400
        assert new_run.name_tag == 'validation_new_name' # name has not been changed

        # "published" validation
        new_run.doi = '1000101010101010'
        new_run.is_archived = True
        new_run.save()

        body = {'save_name': True, 'new_name': 'some_other_name'}
        response = self.client.patch(change_name_url, body,  format='json')

        assert response.status_code == 405   # status 405
        assert new_run.name_tag == 'validation_new_name' # name has not been changed

        # getting back to former settings
        new_run.doi = ''
        new_run.is_archived = False

        # log out the owner and log in other user
        self.client.login(**self.alt_data)
        body = {'save_name': True, 'new_name': 'some_other_name'}
        response = self.client.patch(change_name_url, body,  format='json')

        assert response.status_code == 403  # status 403
        assert new_run.name_tag == 'validation_new_name' # name has not been changed

    def test_archive_result(self):
        archive_url = reverse('Archive results', kwargs={'result_uuid': self.run_id})

        # everything ok, I want to archive ========================================================================
        body = {'archive': True}
        response = self.client.patch(archive_url, body,  format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 200
        assert new_run.is_archived is True

        # everything still ok, now I want to un-archive ==========================================================
        body = {'archive': False}
        response = self.client.patch(archive_url, body,  format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 200
        assert new_run.is_archived is False

        # wrong id =====================================================================
        body = {'archive': False}
        response = self.client.patch(reverse('Archive results', kwargs={'result_uuid': self.wrong_id}), body,  format='json')
        assert response.status_code == 404
        assert new_run.is_archived is False

        # not valid parameter ==========================================================
        body = {'archive': 'some_not_valid_parameter'}
        response = self.client.patch(archive_url, body,  format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 400
        assert new_run.is_archived is False  # nothing has changed

        # not valid method ==========================================================
        body = {'archive': True}
        response = self.client.get(archive_url, body,  format='json')  # should be patch

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 405
        assert new_run.is_archived is False  # nothing has changed

        # you can't modify a published validation ==========================================================
        new_run.doi = '1010101010101'
        new_run.save()

        body = {'archive': True}
        response = self.client.patch(archive_url, body,  format='json')
        assert response.status_code == 405

        new_run.doi = ''
        new_run.save()

        # log out and log in another user to check if only owners should be able to change validations ===============
        self.client.login(**self.alt_data)

        body = {'archive': True}
        response = self.client.patch(archive_url, body,  format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 403
        assert new_run.is_archived is False  # nothing has changed

    def test_extend_result(self):
        extend_result_url = reverse('Extend results', kwargs={'result_uuid': self.run_id})

        # everything ok ==============================================================
        body = {'extend': True}
        response = self.client.patch(extend_result_url, body,  format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)
        new_expiry_date = parser.parse(response.content)

        assert response.status_code == 200
        assert new_expiry_date is not None
        assert new_run.expiry_date == new_expiry_date

        # invalid expiry extension ==================================================
        body = {'extend': False}
        response = self.client.patch(extend_result_url, body,  format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)

        assert response.status_code == 400
        assert new_run.expiry_date == new_expiry_date # nothing has changed

        # wrong id ===================================================================
        body = {'extend': True}
        response = self.client.patch(reverse('Extend results', kwargs={'result_uuid': self.wrong_id}), body,  format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)

        assert response.status_code == 404
        assert new_run.expiry_date == new_expiry_date # nothing has changed

        # published validation =======================================================
        new_run.doi = '1010101019110'
        new_run.save()

        body = {'extend': True}
        response = self.client.patch(extend_result_url, body,  format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 405
        assert new_run.expiry_date == new_expiry_date  # nothing has changed

        new_run.doi = ''
        new_run.save()

        # wrong user =================================================================
        self.client.login(**self.alt_data) # log in as another one

        body = {'extend': True}
        response = self.client.patch(extend_result_url, body,  format='json')
        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 403
        assert new_run.expiry_date == new_expiry_date  # nothing has changed

    @pytest.mark.skipif(not 'DOI_ACCESS_TOKEN_ENV' in os.environ, reason="No access token set in global variables")
    @override_settings(DOI_REGISTRATION_URL="https://sandbox.zenodo.org/api/deposit/depositions")
    def test_publish_result(self):
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
        response = self.client.patch(reverse('Publish result', kwargs={'result_uuid': self.wrong_id}), body, format='json')
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

        assert response.status_code == 400
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

        assert response.status_code == 400
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
        assert not new_run.is_unpublished

    def test_add_validation(self):
        add_validation_url = reverse('Add validation', kwargs={'result_uuid': self.run_id})

        # everything ok
        body = {'add_validation': True}
        response = self.client.post(add_validation_url, body,  format='json')
        print(response)

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 200
        assert len(self.test_user.copied_runs.all()) == 1

        # wrong method
        body = {'add_validation': True}
        response = self.client.patch(add_validation_url, body,  format='json')
        print(response)

        assert response.status_code == 405
        assert len(self.test_user.copied_runs.all()) == 1