import json
import logging
import time
from django.test.utils import override_settings
from django.urls import reverse

import validator.validation as val
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

# Include an appropriate `Authorization:` header on all requests.
from api.tests.test_helper import *
from validator.models import ValidationRun

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
        self.alternative_client = APIClient()

        # start a new validation, which will be used by some tests below
        self.run = default_parameterized_validation(self.test_user)
        self.run.save()
        self.run_id = self.run.id
        val.run_validation(self.run_id)

    def test_stop_validation(self):
        # start a new validation (tcol is run here, because a default one would finish before I cancel it :) )
        run = default_parameterized_validation(self.test_user, tcol=True)
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
        self.alternative_client.login(**self.alt_data)
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

        # save_name == False
        body = {'save_name': False, 'new_name': 'wrong_name'}
        response = self.client.patch(change_name_url, body,  format='json')

        new_run = ValidationRun.objects.get(pk=self.run_id)
        assert response.status_code == 400  # status 400
        assert new_run.name_tag == 'validation_new_name' # name has not been changed

        # "published" validation
        new_run.doi = '1000101010101010'
        new_run.archive = True
        new_run.save()

        body = {'save_name': True, 'new_name': 'some_other_name'}
        response = self.client.patch(change_name_url, body,  format='json')

        assert response.status_code == 405   # status 405
        assert new_run.name_tag == 'validation_new_name' # name has not been changed

        # getting back to former settings
        new_run.doi = ''
        new_run.archive = False

        # log out the owner and log in other user
        self.client.logout()

        self.alternative_client.login(**self.alt_data)
        body = {'save_name': True, 'new_name': 'some_other_name'}
        response = self.client.patch(change_name_url, body,  format='json')

        assert response.status_code == 403  # status 403
        assert new_run.name_tag == 'validation_new_name' # name has not been changed

    # def test_modify_result(self):
    #
    #
    #     modify_result_url = reverse('Modify result', kwargs={'result_uuid': run_id})
    #
    #     # start with PATCH method (DELETE will be later, so there is no need to run the validation twice)
    #
    #     # ================== SAVE NAME =======================



