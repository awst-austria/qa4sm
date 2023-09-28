import logging

from django.urls import reverse

from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *
from validator.models import CopiedValidations
from validator.validation.validation import copy_validationrun


class TestValidationRunView(TestCase):
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables', 'users']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.second_user_data, self.second_test_user = create_alternative_user()

        self.client = APIClient()
        self.client.login(**self.auth_data)

        self.run = create_default_validation_without_running(self.test_user)
        self.run.name_tag = 'B validation'
        self.run.save()

        self.run_2 = create_default_validation_without_running(self.second_test_user)
        self.run_2.name_tag = 'A validation'
        self.run_2.save()

        self.wrong_id = 'f0000000-a000-b000-c000-d00000000000'

    def test_published_results(self):
        published_results_url = reverse('Published results')

        # 'publishing' results
        self.run.doi = '12345/12434'
        self.run.save()
        self.run_2.doi = '108645/12434'
        self.run_2.save()

        # getting all the existing results
        response = self.client.get(published_results_url)
        assert response.status_code == 200
        assert len(response.json()['validations']) == 2
        # this order should be the right one, because the B validation was created first
        assert response.json()['validations'][0]['name_tag'] == 'B validation'
        assert response.json()['validations'][1]['name_tag'] == 'A validation'

        # introducing limit and offset
        response = self.client.get(published_results_url + f'?limit=1&offset=0')
        assert response.status_code == 200
        assert len(response.json()['validations']) == 1  # now there should be only one taken
        assert response.json()['validations'][0]['name_tag'] == 'B validation'

        response = self.client.get(published_results_url + f'?limit=0&offset=0')
        assert response.status_code == 200
        assert len(response.json()['validations']) == 0  # no validations are taken

        response = self.client.get(published_results_url + f'?limit=1&offset=100')
        assert response.status_code == 200
        assert len(response.json()['validations']) == 0  # no validations are taken, because offset is bigger than the
        # validation number

        # introducing order - name_tag
        response = self.client.get(published_results_url + f'?order=name_tag')
        assert response.status_code == 200
        assert response.json()['validations'][0]['name_tag'] == 'A validation'
        assert response.json()['validations'][1]['name_tag'] == 'B validation'

        # changing the order
        response = self.client.get(published_results_url + f'?order=-name_tag')
        assert response.status_code == 200
        assert response.json()['validations'][0]['name_tag'] == 'B validation'
        assert response.json()['validations'][1]['name_tag'] == 'A validation'

        # introducing non existing tag for order
        response = self.client.get(published_results_url + f'?order=-name')
        assert response.status_code == 400
        assert response.json()['message'] == 'Not appropriate order given'

        # logging out and checking access
        self.client.logout()

        # getting all the existing results
        response = self.client.get(published_results_url)
        assert response.status_code == 200
        assert len(response.json()['validations']) == 2
        assert response.json()['validations'][0]['name_tag'] == 'B validation'
        assert response.json()['validations'][1]['name_tag'] == 'A validation'

    def test_my_results(self):
        my_results_url = reverse('My results')

        # getting all the existing results
        response = self.client.get(my_results_url)
        assert response.status_code == 200
        assert len(response.json()['validations']) == 1 # only one because the second one doesn't belong to the logged in user
        # this order should be the right one, because the B validation was created first
        assert response.json()['validations'][0]['name_tag'] == 'B validation'

        # introducing limit and offset
        response = self.client.get(my_results_url + f'?limit=1&offset=0')
        assert response.status_code == 200
        assert len(response.json()['validations']) == 1  # still one
        assert response.json()['validations'][0]['name_tag'] == 'B validation'

        response = self.client.get(my_results_url + f'?limit=0&offset=0')
        assert response.status_code == 200
        assert len(response.json()['validations']) == 0  # no validations are taken

        response = self.client.get(my_results_url + f'?limit=1&offset=100')
        assert response.status_code == 200
        assert len(response.json()['validations']) == 0  # no validations are taken, because offset is bigger than the

        # introducing order - name_tag
        response = self.client.get(my_results_url + f'?order=name_tag')
        assert response.status_code == 200
        assert response.json()['validations'][0]['name_tag'] == 'B validation'

        # introducing non existing tag for order
        response = self.client.get(my_results_url + f'?order=-name')
        assert response.status_code == 400
        assert response.json()['message'] == 'Not appropriate order given'

        # logging out and checking access
        self.client.logout()

        # getting all the existing results
        response = self.client.get(my_results_url)
        assert response.status_code == 403 # no one should have an access to my list

    def test_validation_run_by_id(self):
        validation_run_by_id_url_name = 'Validation run by id' #+ f'id={self.run.id}'

        # take the validation that belongs to the current user:
        response = self.client.get(reverse(validation_run_by_id_url_name, kwargs={'id': self.run.id}))
        assert response.status_code == 200
        assert response.json()['name_tag'] == 'B validation'

        # take the validation that belongs to the other user (it should be possible):
        response = self.client.get(reverse(validation_run_by_id_url_name, kwargs={'id': self.run_2.id}))
        assert response.status_code == 200
        assert response.json()['name_tag'] == 'A validation'

        # take validation as an anonymous client
        self.client.logout()
        response = self.client.get(reverse(validation_run_by_id_url_name, kwargs={'id': self.run.id}))
        assert response.status_code == 200
        assert response.json()['name_tag'] == 'B validation'

        # try to take non-existing validation:
        response = self.client.get(reverse(validation_run_by_id_url_name, kwargs={'id': self.wrong_id}))
        assert response.status_code == 404

    def test_custom_tracked_validation_runs(self):
        tracked_validations_url = reverse('Tracked custom run')

        # should work, but there are no tracked validations so it will be 0

        response = self.client.get(tracked_validations_url)
        assert response.status_code == 200
        assert len(response.json()) == 0

        tracked_val = CopiedValidations(used_by_user=self.test_user, original_run=self.run_2, copied_run=self.run_2)
        tracked_val.save()

        # Now, the logged in user tracks a validation:
        response = self.client.get(tracked_validations_url)
        assert response.status_code == 200
        assert len(response.json()) == 1

        # now the second user also tracks a validation
        tracked_val = CopiedValidations(used_by_user=self.second_test_user, original_run=self.run, copied_run=self.run)
        tracked_val.save()
        # so there are two validations in the CopiedValidation table
        assert len(CopiedValidations.objects.all()) == 2
        # but the logged in user can see only his tracked validation
        response = self.client.get(tracked_validations_url)
        assert response.status_code == 200
        assert len(response.json()) == 1

        # now I copy validation to check if the view returns only the ones that are tracked
        copy_validationrun(ValidationRun.objects.get(pk=self.run_2.id), self.test_user)

        # # now CopiedValidation table should contain 3 instances
        assert len(CopiedValidations.objects.all()) == 3
        #
        # but the copy validation should not be found as a tracked one
        response = self.client.get(tracked_validations_url)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['id'] == str(self.run_2.id)

        # now I log out to check if the view is available only for logged in users
        self.client.logout()
        response = self.client.get(tracked_validations_url)
        assert response.status_code == 403

    def test_get_copied_validations(self):
        # validation copied
        copied_run = copy_validationrun(ValidationRun.objects.get(pk=self.run_2.id), self.test_user)
        copied_run_url_name = 'Copied run record'

        # everything is ok
        response = self.client.get(reverse(copied_run_url_name, kwargs={'id': copied_run['run_id']}))
        assert response.status_code == 200
        assert response.json()['original_run'] == str(self.run_2.id)

        # wrong id
        response = self.client.get(reverse(copied_run_url_name, kwargs={'id': self.wrong_id}))
        assert response.status_code == 404

        # another user - they should have an access, because this method is used to pass information about a validation,
        # and we allow sharing validations between users
        self.client.login(**self.second_user_data)
        response = self.client.get(reverse(copied_run_url_name, kwargs={'id': copied_run['run_id']}))
        assert response.status_code == 200
        assert response.json()['original_run'] == str(self.run_2.id)





