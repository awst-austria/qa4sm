import logging

from django.contrib.auth import get_user_model
User = get_user_model()
from django.core import mail as mail
from django.test import TestCase

import validator.mailer as val_mail
from validator.models import ValidationRun

class DontMailMe(object):
    """
    Helper class to test mailing errors, used in unit tests.
    """

class TestMailer(TestCase):

    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.user_data = {
            'username': 'chuck_norris',
            'password': 'roundhousekick',
            'email': 'norris@awst.at',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            }
        self.testuser = User.objects.create_user(**self.user_data)

    def check_outbox(self):
        self.assertEqual(len(mail.outbox), 1)
        assert mail.outbox[0]
        assert mail.outbox[0].subject
        assert mail.outbox[0].to
        assert mail.outbox[0].from_email
        assert mail.outbox[0].body

        self.__logger.debug(mail.outbox[0].from_email)
        self.__logger.debug(mail.outbox[0].to)
        self.__logger.debug(mail.outbox[0].subject)
        self.__logger.debug(mail.outbox[0].body)

    def test_val_finished(self):
        run = ValidationRun()
        run.user = self.testuser
        val_mail.send_val_done_notification(run)
        self.check_outbox()

    def test_user_signup(self):
        val_mail.send_new_user_signed_up(self.testuser)
        self.check_outbox()

    def test_user_activation(self):
        val_mail.send_user_status_changed(self.testuser, activate=True)
        self.check_outbox()

    def test_user_deactivation(self):
        val_mail.send_user_status_changed(self.testuser, activate=False)
        self.check_outbox()

    def test_error(self):
        val_mail._send_email(['noreply@awst.at'], None, DontMailMe())
