import logging
import shutil
import time

from django.conf import settings
from django.urls import reverse

import validator.validation as val
from django.test import TestCase
from rest_framework.test import APIClient

from api.tests.test_helper import *
from validator.validation import mkdir_if_not_exists, set_outfile

User = get_user_model()


class TestUserView(TestCase):
    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        # self.client.login(**self.auth_data)

        # self.run = create_default_validation_without_running(self.test_user)
        # self.run.save()

    def test_signup_post(self):
        signup_url = reverse('Sign up')
        # no username provided
        user_form_correct = {'username': '',
                             'password1':'roachRoach',
                             'password2':'roachRoach',
                             'email': 'geralt@of.rivia.pl',
                             'first_name': 'Geralt',
                             'last_name': 'TheWitcher',
                             'organisation': 'Kaer Morhen',
                             'country': 'PL',
                             'orcid': '',
                             'terms_consent': True}
        response = self.client.post(signup_url, user_form_correct, format='json')
        assert response.status_code == 400
        assert len(User.objects.filter(email='geralt@of.rivia.pl')) == 0

        # no email provided
        user_form_correct = {'username': 'geralt_of_rivia',
                             'password1':'roachRoach',
                             'password2':'roachRoach',
                             'email': '',
                             'first_name': 'Geralt',
                             'last_name': 'TheWitcher',
                             'organisation': 'Kaer Morhen',
                             'country': 'PL',
                             'orcid': '',
                             'terms_consent': True}
        response = self.client.post(signup_url, user_form_correct, format='json')
        assert response.status_code == 400
        assert len(User.objects.filter(username='geralt_of_rivia')) == 0

        # not matching passwords
        user_form_correct = {'username': 'geralt_of_rivia',
                             'password1':'roachRoach',
                             'password2':'roach',
                             'email': 'geralt@of.rivia.pl',
                             'first_name': 'Geralt',
                             'last_name': 'TheWitcher',
                             'organisation': 'Kaer Morhen',
                             'country': 'PL',
                             'orcid': '',
                             'terms_consent': True}
        response = self.client.post(signup_url, user_form_correct, format='json')
        assert response.status_code == 400
        assert len(User.objects.filter(username='geralt_of_rivia')) == 0

        # no consent
        user_form_correct = {'username': 'geralt_of_rivia',
                             'password1':'roach',
                             'password2':'roach',
                             'email': 'geralt@of.rivia.pl',
                             'first_name': 'Geralt',
                             'last_name': 'TheWitcher',
                             'organisation': 'Kaer Morhen',
                             'country': 'PL',
                             'orcid': '',
                             'terms_consent': False}
        response = self.client.post(signup_url, user_form_correct, format='json')
        assert response.status_code == 400
        assert len(User.objects.filter(username='geralt_of_rivia')) == 0

        # too short password
        user_form_correct = {'username': 'geralt_of_rivia',
                             'password1':'roach',
                             'password2':'roach',
                             'email': 'geralt@of.rivia.pl',
                             'first_name': 'Geralt',
                             'last_name': 'TheWitcher',
                             'organisation': 'Kaer Morhen',
                             'country': 'PL',
                             'orcid': '',
                             'terms_consent': True}
        response = self.client.post(signup_url, user_form_correct, format='json')
        assert response.status_code == 400
        assert len(User.objects.filter(username='geralt_of_rivia')) == 0

        # incorrect orcid
        user_form_correct = {'username': 'geralt_of_rivia',
                             'password1':'roachRoach',
                             'password2':'roachRoach',
                             'email': 'geralt@of.rivia.pl',
                             'first_name': 'Geralt',
                             'last_name': 'TheWitcher',
                             'organisation': 'Kaer Morhen',
                             'country': 'PL',
                             'orcid': '1111',
                             'terms_consent': True}
        response = self.client.post(signup_url, user_form_correct, format='json')
        assert response.status_code == 400
        assert len(User.objects.filter(username='geralt_of_rivia')) == 0

        # correct full user form
        user_form_correct = {'username': 'geralt_of_rivia',
                             'password1':'roachRoach',
                             'password2':'roachRoach',
                             'email': 'geralt@of.rivia.pl',
                             'first_name': 'Geralt',
                             'last_name': 'TheWitcher',
                             'organisation': 'Kaer Morhen',
                             'country': 'PL',
                             'orcid': '0000-0002-1111-0097',
                             'terms_consent': True}
        response = self.client.post(signup_url, user_form_correct, format='json')
        new_user = User.objects.get(username='geralt_of_rivia')

        assert response.status_code == 200
        assert new_user
        assert not new_user.is_active # the account has been created but not activated

        # correct full user form - but the user already exists
        user_form_correct = {'username': 'geralt_of_rivia',
                             'password1':'roachRoach',
                             'password2':'roachRoach',
                             'email': 'geralt@of.rivia.pl',
                             'first_name': 'Geralt',
                             'last_name': 'TheWitcher',
                             'organisation': 'Kaer Morhen',
                             'country': 'PL',
                             'orcid': '0000-0002-1111-0097',
                             'terms_consent': True}
        response = self.client.post(signup_url, user_form_correct, format='json')

        assert response.status_code == 400

        # correct minimum user form
        user_form_correct = {'username': 'geraltOfRivia',
                             'password1':'roachRoach',
                             'password2':'roachRoach',
                             'email': 'geralt@of.rivia.pl',
                             'first_name': '',
                             'last_name': '',
                             'organisation': '',
                             'country': '',
                             'orcid': '',
                             'terms_consent': True}
        response = self.client.post(signup_url, user_form_correct, format='json')
        new_user = User.objects.get(username='geraltOfRivia')

        assert response.status_code == 200
        assert new_user
        assert not new_user.is_active # the account has been created but not activated

    def test_user_update(self):
        user_update_url = reverse('User update')
        self.client.login(**self.auth_data)

        # correct data - no password change
        user_data = {
            'username': self.auth_data['username'],
            'password1': '',
            'password2': '',
            'email': 'geralt@awst.at',
            'first_name': 'Geralt',
            'last_name': 'TheWitcher',
            'organisation': 'Kaer Morhen',
            'country': 'PL',
            'orcid': '0000-0002-1111-0097',
            'terms_consent': True
        }

        response = self.client.patch(user_update_url, user_data, format='json')
        assert response.status_code == 200
        assert User.objects.get(username=self.auth_data['username']).email == 'geralt@awst.at'

        # remove all non required data
        user_data = {
            'username': self.auth_data['username'],
            'password1': '',
            'password2': '',
            'email': 'geralt@awst.at',
            'first_name': '',
            'last_name': '',
            'organisation': '',
            'country': '',
            'orcid': '',
            'terms_consent': True
        }

        response = self.client.patch(user_update_url, user_data, format='json')
        assert response.status_code == 200
        assert User.objects.get(username=self.auth_data['username']).first_name == ''

        # change your password
        old_password = User.objects.get(username=self.auth_data['username']).password
        user_data = {
            'username': self.auth_data['username'],
            'password1': 'myNewWordPass',
            'password2': 'myNewWordPass',
            'email': 'geralt@awst.at',
            'first_name': '',
            'last_name': '',
            'organisation': '',
            'country': '',
            'orcid': '',
            'terms_consent': True
        }

        response = self.client.patch(user_update_url, user_data, format='json')
        assert response.status_code == 200
        assert User.objects.get(username=self.auth_data['username']).password != old_password

        # try to remove email
        user_data = {
            'username': self.auth_data['username'],
            'password1': '',
            'password2': '',
            'email': 'geralt@awst.at',
            'first_name': '',
            'last_name': '',
            'organisation': '',
            'country': '',
            'orcid': '',
            'terms_consent': True
        }

        response = self.client.patch(user_update_url, user_data, format='json')
        assert response.status_code == 400
        assert User.objects.get(username=self.auth_data['username']).email == 'geralt@awst.at' # still the same email

        # try to introduce wrong orcid
        user_data = {
            'username': self.auth_data['username'],
            'password1': '',
            'password2': '',
            'email': '',
            'first_name': '',
            'last_name': '',
            'organisation': '',
            'country': '',
            'orcid': '1111',
            'terms_consent': True
        }

        response = self.client.patch(user_update_url, user_data, format='json')
        assert response.status_code == 400
        assert User.objects.get(username=self.auth_data['username']).orcid == ''  # still the same email

