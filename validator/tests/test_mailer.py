from datetime import datetime, timedelta
import logging

from dateutil.tz.tz import tzlocal
from django.contrib.auth import get_user_model
User = get_user_model()

from django.core import mail as mail
from django.test import TestCase

from django.conf import settings
import validator.mailer as val_mail
from validator.models import DataVariable
from validator.models import Dataset
from validator.models import DatasetConfiguration
from validator.models import DatasetVersion
from validator.models import ValidationRun
from validator.validation import globals


class DontMailMe(object):
    """
    Helper class to test mailing errors, used in unit tests.
    """

class TestMailer(TestCase):

    __logger = logging.getLogger(__name__)

    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

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
        test_datasets = [Dataset.objects.get(short_name=globals.C3SC),
                         Dataset.objects.get(short_name=globals.ASCAT),
                         Dataset.objects.get(short_name=globals.SMAP_L3),]

        run = ValidationRun()
        run.start_time = datetime.now(tzlocal())
        run.end_time = datetime.now(tzlocal())
        run.user = self.testuser
        run.save()

        for ds in test_datasets:
            data_c = DatasetConfiguration()
            data_c.validation = run
            data_c.dataset = ds
            data_c.version = ds.versions.first()
            data_c.variable = data_c.version.variables.first()
            data_c.save()

        ref_c = DatasetConfiguration()
        ref_c.validation = run
        ref_c.dataset = Dataset.objects.get(short_name='ISMN')
        ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
        ref_c.variable = DataVariable.objects.get(pretty_name='ISMN_soil_moisture')
        ref_c.save()

        run.spatial_reference_configuration = ref_c
        run.temporal_reference_configuration = ref_c
        run.scaling_ref = ref_c
        run.save()

        val_mail.send_val_done_notification(run)
        self.check_outbox()

    def test_val_expired(self):
        run = ValidationRun()
        now = datetime.now(tzlocal())
        run.start_time = now - timedelta(days=settings.VALIDATION_EXPIRY_DAYS - settings.VALIDATION_EXPIRY_WARNING_DAYS)
        run.end_time = run.start_time + timedelta(days=1)
        run.user = self.testuser
        run.save()
        assert not run.expiry_notified

        val_mail.send_val_expiry_notification([run])
        self.check_outbox()

        assert ValidationRun.objects.get(pk=run.id).expiry_notified

        # multiple validations in one email:
        run = ValidationRun()
        now = datetime.now(tzlocal())
        run.start_time = now - timedelta(days=settings.VALIDATION_EXPIRY_DAYS - settings.VALIDATION_EXPIRY_WARNING_DAYS)
        run.end_time = run.start_time + timedelta(days=1)
        run.user = self.testuser
        run.save()
        assert not run.expiry_notified

        run_2 = ValidationRun()
        now = datetime.now(tzlocal())
        run_2.start_time = now - timedelta(days=settings.VALIDATION_EXPIRY_DAYS - settings.VALIDATION_EXPIRY_WARNING_DAYS)
        run_2.end_time = run_2.start_time + timedelta(days=1)
        run_2.user = self.testuser
        run_2.save()
        assert not run_2.expiry_notified

        val_mail.send_val_expiry_notification([run, run_2])

        assert ValidationRun.objects.get(pk=run.id).expiry_notified
        assert ValidationRun.objects.get(pk=run_2.id).expiry_notified

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

    def test_autocleanup_failed(self):
        val_mail.send_autocleanup_failed('Auto cleanup script could not be run.')
        self.check_outbox()