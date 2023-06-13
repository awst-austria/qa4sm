import logging
from django.urls import reverse

from django.test import TestCase
from rest_framework.test import APIClient

from api.tests.test_helper import *
from django.core import mail
from django.conf import settings

User = get_user_model()


class TestUserView(TestCase):
    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_send_support_request(self):
        support_request_url = reverse('Support request')
        contact_form_correct_no_copy = {
            'name': 'John Doe',
            'email': 'johndoe@awst.at',
            'content': "I need your help with QA4SM",
            'send_copy_to_user': False,
            'active': False,
            'honeypot': 100
        }

        contact_form_correct_copy = {
            'name': 'John Doe',
            'email': 'johndoe@awst.at',
            'content': "I need your help with QA4SM",
            'send_copy_to_user': True,
            'active': False,
            'honeypot': 100
        }

        contact_form_bot_1 = {
            'name': 'John Doe',
            'email': 'johndoe@awst.at',
            'content': "I need your help with QA4SM",
            'send_copy_to_user': True,
            'active': True,
            'honeypot': 0
        }

        contact_form_bot_2 = {
            'name': 'John Doe',
            'email': 'johndoe@awst.at',
            'content': "I need your help with QA4SM",
            'send_copy_to_user': True,
            'active': False,
            'honeypot': 0
        }

        contact_form_bot_3 = {
            'name': 'John Doe',
            'email': 'johndoe@awst.at',
            'content': "I need your help with QA4SM",
            'send_copy_to_user': True,
            'active': True,
            'honeypot': 100
        }

        # proper form sent, but without a copy to the user
        response = self.client.post(support_request_url, contact_form_correct_no_copy, format='json')
        assert response.status_code == 200
        assert len(mail.outbox) == 1

        sent_mail = mail.outbox[0]
        assert sent_mail
        assert sent_mail.subject == "[USER MESSAGE] - Sent via contact form"
        assert sent_mail.body
        assert sent_mail.from_email == settings.EMAIL_FROM
        assert sent_mail.to[0] == settings.EMAIL_FROM
        assert len(sent_mail.to) == 1

        # proper form, but with a copy to the user this time
        response = self.client.post(support_request_url, contact_form_correct_copy, format='json')

        assert response.status_code == 200
        assert len(mail.outbox) == 3  # I don't clean this mailbox, so there are already three emails
        sent_mail = mail.outbox[1]
        sent_copy = mail.outbox[2]

        assert sent_mail.from_email == settings.EMAIL_FROM
        assert sent_mail.to[0] == settings.EMAIL_FROM
        assert sent_copy.to[0] == contact_form_correct_copy.get('email')

        # improper form number 1
        response = self.client.post(support_request_url, contact_form_bot_1, format='json')

        assert response.status_code == 400
        assert len(mail.outbox) == 3  # still only three emails, as no email get sent

        # improper form number 2
        response = self.client.post(support_request_url, contact_form_bot_2, format='json')

        assert response.status_code == 400
        assert len(mail.outbox) == 3  # still only three emails, as no email get sent

        # improper form number 3
        response = self.client.post(support_request_url, contact_form_bot_3, format='json')

        assert response.status_code == 400
        assert len(mail.outbox) == 3  # still only three emails, as no email get sent
