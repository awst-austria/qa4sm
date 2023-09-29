import time

from celery.app import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
import pytest
import logging
from django.test import TestCase
from django.urls.base import reverse

from valentina.celery import app
from validator.models import Settings



@shared_task(bind=True)
def execute_test_job(self, parameter):
    print(parameter)
    time.sleep(10)

## See also: https://stackoverflow.com/a/11887308/
class TestAdmin(TestCase):

    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

    __logger = logging.getLogger(__name__)
    # setting False, because the page that we refer here may raise logging.exception and pytest 6.0.0 and newer
    # does not handle it
    logging.raiseExceptions = False

    def setUp(self):
        self.user_credentials = {
            'username': 'testuser',
            'password': 'secret',
            'is_staff' : False,
            'is_active' : True,
        }
        self.testuser = User.objects.create_user(**self.user_credentials)

        self.staff_credentials = {
            'username': 'dilbert',
            'password': 'treblid',
            'is_staff' : True,
        }
        self.teststaff = User.objects.create_user(**self.staff_credentials)

        self.admin_credentials = {
            'username': 'chuck_norris',
            'password': 'superpassword!',
            'is_staff' : True,
            'is_superuser' : True,
        }
        self.testadmin = User.objects.create_user(**self.admin_credentials)

    def test_access_control(self):
        login_url = reverse('admin:login')
        urls = [
            reverse('admin:index'),
            reverse('admin:validator_validationrun_changelist'),
            reverse('admin:validator_user_changelist'),
            reverse('admin:validator_user_change', kwargs={'object_id': self.testuser.id}),
            reverse('admin:user_change_status', kwargs={'user_id': self.testuser.id}),
            ]

        for url in urls:
            self.__logger.info(url)

            # anonymous
            self.client.logout()
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, '{}?next={}'.format(login_url, url))
            response = self.client.post(url, follow=True)
            self.assertRedirects(response, '{}?next={}'.format(login_url, url))

            # as normal user
            self.client.login(**self.user_credentials)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, '{}?next={}'.format(login_url, url))

            # as staff
            self.client.login(**self.staff_credentials)
            response = self.client.get(url)
            if url == reverse('admin:index'):
                self.assertEqual(response.status_code, 200)
            else:
                self.assertEqual(response.status_code, 403)

            # as superuser
            self.client.login(**self.admin_credentials)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    @pytest.mark.needs_advanced_setup
    def test_queue_page(self):
        ## we can only run this test if we have a celery env set up
        if (hasattr(settings, 'CELERY_TASK_ALWAYS_EAGER') and settings.CELERY_TASK_ALWAYS_EAGER):
            return

        queue_name = 'unittestqueue'

        url = reverse('admin:system-settings')

        # first, try accessing page without login - should fail
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '{}?next={}'.format(reverse('admin:login'), url))

        ## add a queue so that the queue page has something to show
        app.control.add_consumer(queue_name, reply=True)
        ## start a job so that it can be listed on the queue page
        execute_test_job.apply_async(args=['hello'], queue=queue_name)

        ## make sure the queue page works
        self.client.login(**self.admin_credentials)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        ## check the contents of the queue page via its "context" variable
        assert response.context['workers']
        workers = response.context['workers'][0]
        print(workers)

        assert workers['name'] is not None
        assert workers['queues'] is not None
        assert workers['active_tasks'] is not None
        assert workers['scheduled_tasks'] is not None

        ## the queue we added must show on the page
        assert queue_name in workers['queues']

        ## the job we started should be listed as active
#         assert workers['active_tasks'] > 0

    def test_maintenance_mode_switching(self):
        # store state to revert back at the end of the test
        orig_mm = Settings.load().maintenance_mode

        url = reverse('admin:system-settings')

        # switch maintenance mode to a string, empty string, on, off, and back to original state
        for mode in ['anything', '', True, False, orig_mm]:
            maint_params = { 'maintenance_mode': mode, }
            self.client.login(**self.admin_credentials)
            response = self.client.post(url, maint_params, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Settings.load().maintenance_mode, bool(mode))

    # this test doesn't make sense anymore, as the parameters are sent in frontend, I'll remove it later when I rewrite it
    # def test_maintenance_mode_redirection(self):
    #     validation_params = {
    #         'datasets-TOTAL_FORMS': 1,
    #         'datasets-INITIAL_FORMS': 1,
    #         'datasets-MIN_NUM_FORMS': 1,
    #         'datasets-MAX_NUM_FORMS': 5,
    #         'datasets-0-dataset': Dataset.objects.get(short_name=globals.C3SC).id,
    #         'datasets-0-version': DatasetVersion.objects.get(short_name=globals.C3S_V201706).id,
    #         'datasets-0-variable': DataVariable.objects.get(short_name=globals.C3S_sm).id,
    #         'ref-dataset': Dataset.objects.get(short_name=globals.ISMN).id,
    #         'ref-version': DatasetVersion.objects.get(short_name=globals.ISMN_V20180712_MINI).id,
    #         'ref-variable': DataVariable.objects.get(short_name=globals.ISMN_soil_moisture).id,
    #         'scaling_method': ValidationRun.MEAN_STD,
    #         #'scaling_ref': ValidationRun.SCALE_REF,
    #     }
    #
    #     # store state to revert back at the end of the test
    #     settings = Settings.load()
    #     orig_mm = settings.maintenance_mode
    #
    #     url = reverse('admin:system-settings')
    #     validation_url = get_angular_url('validate')
    #
    #     # switch on maint mode
    #     maint_params = { 'maintenance_mode': True, }
    #     self.client.login(**self.admin_credentials)
    #     self.client.post(url, maint_params, follow=True)
    #     self.client.logout()
    #
    #     # try to run a validation as a regular user
    #     self.client.login(**self.user_credentials)
    #     result = self.client.post(validation_url, validation_params)
    #
    #     # check that we're redirected back to the validation page
    #     self.assertRedirects(result, validation_url)
    #
    #     settings.maintenance_mode = orig_mm
    #     settings.save()

    def test_change_user_status(self):
        url = reverse('admin:user_change_status', kwargs={'user_id': self.testuser.id})
        change_params = {
            'status_action': 'deactivate',
            'send_email': True,
        }

        # deactivate testuser and try it twice (second time should have no effect
        for idx in range(2):
            print(idx)
            self.client.login(**self.admin_credentials)
            response = self.client.post(url, change_params, follow=True)
            self.assertEqual(response.status_code, 200)
            changed_user = User.objects.get(id=self.testuser.id)
            assert changed_user.is_active == False

        # switch to activation
        change_params['status_action'] = 'activate'

        # reactivate testuser and try it twice (second time should have no effect
        for idx in range(2):
            print(idx)
            response = self.client.post(url, change_params, follow=True)
            self.assertEqual(response.status_code, 200)
            changed_user = User.objects.get(id=self.testuser.id)
            assert changed_user.is_active == True

    def test_change_user_status_empty_post(self):
        url = reverse('admin:user_change_status', kwargs={'user_id': self.testuser.id})

        self.client.login(**self.admin_credentials)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_change_user_status_no_user(self):
        url = reverse('admin:user_change_status', kwargs={'user_id': 0})

        self.client.login(**self.admin_credentials)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_change_user_bulk_actions(self):
        bulk_actions = {
            'bulk_user_activation' : True,
            'bulk_user_deactivation' : False,
            'silent_bulk_user_activation' : True,
            'silent_bulk_user_deactivation' : False,
            }

        url = reverse('admin:validator_user_changelist')
        change_params = {
            '_selected_action': self.testuser.id,
            'action': 'bulk_user_activation',
        }
        self.client.login(**self.admin_credentials)

        for action, state in bulk_actions.items():
            change_params['action'] = action
            response = self.client.post(url, change_params, follow=True)
            self.assertEqual(response.status_code, 200)
            changed_user = User.objects.get(id=self.testuser.id)
            assert changed_user.is_active == state

    def test_change_user_bulk_actions_mock_error(self):
        bulk_actions = {
            'bulk_user_deactivation' : False,
            'bulk_user_activation' : True,
            'silent_bulk_user_deactivation' : False,
            'silent_bulk_user_activation' : True,
            }

        url = reverse('admin:validator_user_changelist')
        change_params = {
            '_selected_action': self.testuser.id,
            'action': 'bulk_user_activation',
        }
        self.client.login(**self.admin_credentials)

        for action, state in bulk_actions.items():
            print(action)
            change_params['action'] = action
            response = self.client.post(url, change_params, follow=True)
            self.assertEqual(response.status_code, 200)
            changed_user = User.objects.get(id=self.testuser.id)
            assert changed_user.is_active == state
