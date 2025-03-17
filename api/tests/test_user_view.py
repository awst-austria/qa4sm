import logging
from django.urls import reverse

from django.test import TestCase
from rest_framework.test import APIClient

from api.frontend_urls import get_angular_url
from api.tests.test_helper import *
from django.core import mail
from django.conf import settings
from re import findall as regex_find
User = get_user_model()


class TestUserView(TestCase):
    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()

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
                             'terms_consent': True,
                             'active': False,
                             'honeypot': 100}
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
                             'terms_consent': True,
                             'active': False,
                             'honeypot': 100}
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
                             'terms_consent': True,
                             'active': False,
                             'honeypot': 100}
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
                             'terms_consent': False,
                             'active': False,
                             'honeypot': 100}
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
                             'terms_consent': True,
                             'active': False,
                             'honeypot': 100}
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
                             'terms_consent': True,
                             'active': False,
                             'honeypot': 100}
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
                             'terms_consent': True,
                             'active': False,
                             'honeypot': 100}
        response = self.client.post(signup_url, user_form_correct, format='json')
        new_user = User.objects.get(username='geralt_of_rivia')

        assert response.status_code == 200
        assert new_user
        assert not new_user.is_active # the account has been created but not activated

        verification_email = mail.outbox[0]

        # check content of verification email
        assert verification_email
        assert verification_email.subject
        assert verification_email.body
        assert verification_email.from_email == settings.EMAIL_FROM
        assert new_user.email in verification_email.to
        assert any(name in verification_email.body for name in [new_user.first_name, new_user.username]) # can be either name or username


        urls = regex_find(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                           verification_email.body)
        verification_url = urls[0]
        
        # Test verification endpoint
        response = self.client.get(verification_url)
        assert response.status_code == 302  
        
        # Check user activation worked
        new_user.refresh_from_db()
        assert new_user.is_active

        # Assert token is invalid after activation
        response = self.client.get(verification_url)
        assert response.status_code == 302
        assert 'error' in response.url  

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
                             'terms_consent': True,
                             'active': False,
                             'honeypot': 100}
        response = self.client.post(signup_url, user_form_correct, format='json')

        assert response.status_code == 400

        # correct full user form - but bot field checked
        user_form_correct = {'username': 'geralt_from_rivia',
                             'password1':'roachRoach',
                             'password2':'roachRoach',
                             'email': 'geralt@of.rivia.pl',
                             'first_name': 'Geralt',
                             'last_name': 'TheWitcher',
                             'organisation': 'Kaer Morhen',
                             'country': 'PL',
                             'orcid': '0000-0002-1111-0097',
                             'terms_consent': True,
                             'active': True,
                             'honeypot': 100}
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
                             'terms_consent': True,
                             'active': False,
                             'honeypot': 100}
        response = self.client.post(signup_url, user_form_correct, format='json')
        new_user = User.objects.get(username='geraltOfRivia')

        assert response.status_code == 200
        assert new_user
        assert not new_user.is_active # the account has been created but not activated

    def test_update_password(self):
        # change your password
        password_update_url = reverse('Password Update')
        self.client.login(**self.auth_data)

        old_password = User.objects.get(username=self.auth_data['username']).password
        user_data = {
            'old_password': self.auth_data['password'],
            'new_password': 'myNewWordPass',
            'confirm_password': 'myNewWordPass',
        }

        response = self.client.post(password_update_url, user_data, format='json')
        assert response.status_code == 200
        assert User.objects.get(username=self.auth_data['username']).password != old_password

        user_data_wrong_password = {
            'old_password': 'notTheProperPassword',
            'new_password': 'myNewWordPass',
            'confirm_password': 'myNewWordPass',
        }

        response = self.client.post(user_data_wrong_password, user_data, format='json')
        assert response.status_code == 404


        user_data_non_matching_passwords = {
            'old_password': 'myNewWordPass',
            'new_password': 'brandNewPassword1209',
            'confirm_password': 'almostTheSame',
        }

        response = self.client.post(user_data_non_matching_passwords, user_data, format='json')
        assert response.status_code == 404

        user_data_not_appropriate_password= {
            'old_password': 'myNewWordPass',
            'new_password': '12345',
            'confirm_password': '12345',
        }

        response = self.client.post(user_data_not_appropriate_password, user_data, format='json')
        assert response.status_code == 404


    def test_user_update(self):
        user_update_url = reverse('User update')
        self.client.login(**self.auth_data)

        # correct data - no password change
        user_data = {
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

        # try to remove email
        user_data = {
            'email': '',
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
            'email': 'geralt@awst.at',
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

    def test_user_delete(self):
        user_delete_url = reverse('User delete')
        # log in
        self.client.login(**self.auth_data)
        # check if the user is active
        assert self.test_user.is_active
        # send delete request
        response = self.client.delete(user_delete_url)
        # refresh the user
        self.test_user.refresh_from_db()

        assert response.status_code == 200
        assert not self.test_user.is_active  # user is not active anymore
        assert not self.client.login(**self.auth_data)  # and they can not login
        assert User.objects.get(username=self.auth_data['username']) # but the account still exists

    def test_password_reset(self):
        ## pattern to get the password reset link from the email
        reset_url_pattern = get_angular_url('validate-token', 'DUMMY')
        reset_url_pattern = reset_url_pattern.replace('DUMMY', '([^/]+)')
        reset_submit_url = reverse('password_reset:reset-password-request') # reset-password-request comes from the package
        submit_new_password_url = reverse('password_reset:reset-password-confirm')
        validate_token_url = reverse('password_reset:reset-password-validate')

        original_password = self.auth_data['password']

        # method get is not allowed here
        response = self.client.get(reset_submit_url, follow=True)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reset_submit_url, {'email': self.test_user.email})
        self.assertEqual(response.status_code, 200)

        sent_mail = mail.outbox[0]

        assert sent_mail
        assert sent_mail.subject
        assert sent_mail.body
        assert sent_mail.from_email == settings.EMAIL_FROM
        assert self.test_user.email in sent_mail.to
        assert self.test_user.username in sent_mail.body

        # assert False

        ## check that the email contains a confirmation link with userid and token
        urls = regex_find(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                          sent_mail.body)
        token = None
        for u in urls:
            rmatch = regex_find(reset_url_pattern, u)
            if rmatch:
                token = rmatch[0]

        assert token

        # try to submit invalid password
        response = self.client.post(submit_new_password_url, {'password': '123456', 'token': token})
        assert response.status_code == 400
        assert response.json()['password'][0] == 'This password is too short. It must contain at least 8 characters.'
        assert response.json()['password'][1] == 'This password is too common.'
        assert response.json()['password'][2] == 'This password is entirely numeric.'

        ## now try to use the link in the email several times - should only be successful the first time
        for i in range(1, 3):
            # validate token from the email
            response = self.client.post(validate_token_url, {'token': token})
            ## first time
            if i == 1:
                self.assertEqual(response.status_code, 200)
                # If the token is ok, the website is redirected to the new password form which sends
                # new password and the token (password and password confirmation are validated in the frontend part)
                self.auth_data['password'] = '1superPassword!!'
                response = self.client.post(submit_new_password_url, {'password': self.auth_data['password'], 'token': token})
                assert response.status_code == 200
            ## second time
            else:
                ## token is no more valid
                self.assertEqual(response.status_code, 404)

                # so there is no possibility ot submit a new password
                response = self.client.post(submit_new_password_url, {'password': '1superPassword!!', 'token': token})
                assert response.status_code == 404


        ## make sure we can log in with the new password
        login_success = self.client.login(**self.auth_data)
        assert login_success

        ## make sure we can't log in with the old password
        login_success = self.client.login(**{'username': self.auth_data['username'], 'password': original_password})
        assert not login_success