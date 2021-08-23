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

