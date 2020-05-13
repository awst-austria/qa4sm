'''
Test our custom django commands
'''

from datetime import datetime, timedelta
import logging

from dateutil.tz.tz import tzlocal
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from validator.models import ValidationRun


# See https://stackoverflow.com/a/6513372/
class TestCommands(TestCase):

    __logger = logging.getLogger(__name__)

    def setUp(self):
        user_data = {
            'username': 'testuser',
            'password': 'secret',
            'email': 'noreply@awst.at',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            }

        try:
            self.testuser = User.objects.get(username=user_data['username'])
        except User.DoesNotExist:
            self.testuser = User.objects.create_user(**user_data)

    def test_abortrunningvalidations(self):
        # make sure we don't have real running validations
        running_validations = ValidationRun.objects.filter(progress__range=(0, 99))
        assert not running_validations

        # make sure we have a fake running validation for testing
        run = ValidationRun()
        run.start_time = datetime.now(tzlocal())
        run.progress = 50
        run.save()
        run_id = run.id
        running_validations = ValidationRun.objects.filter(progress__range=(0, 99))
        assert running_validations

        # run the command
        args = []
        opts = {}
        call_command('abortrunningvalidations', *args, **opts)

        # make sure that our test validation was marked as failed
        running_validations = ValidationRun.objects.filter(progress__range=(0, 99))
        assert not running_validations
        test_val = ValidationRun.objects.get(id=run_id)
        assert test_val
        assert test_val.end_time
        assert test_val.progress == -1

    def test_autocleanupvalidations(self):

        ended_vals = ValidationRun.objects.filter(end_time__isnull=False).count()

        ## unexpired validation
        run1 = ValidationRun()
        run1.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
        run1.end_time = timezone.now()
        run1.user = self.testuser
        run1.save()
        runid1 = run1.id

        ## 20% of warning period has passed
        run2 = ValidationRun()
        run2.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
        run2.end_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS - settings.VALIDATION_EXPIRY_WARNING_DAYS * 0.8)
        run2.user = self.testuser
        run2.save()
        runid2 = run2.id

        ## 80% of warning period has passed
        run3 = ValidationRun()
        run3.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
        run3.end_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS - settings.VALIDATION_EXPIRY_WARNING_DAYS * 0.2)
        run3.user = self.testuser
        run3.save()
        runid3 = run3.id

        ## just expired validation
        run4 = ValidationRun()
        run4.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
        run4.end_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS)
        run4.user = self.testuser
        run4.save()
        runid4 = run4.id

        ## long expired validation
        run5 = ValidationRun()
        run5.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
        run5.end_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 2)
        run5.user = self.testuser
        run5.save()
        runid5 = run5.id

        ended_vals2 = ValidationRun.objects.filter(end_time__isnull=False).count()
        assert ended_vals + 5 == ended_vals2
        assert runid1
        assert runid2
        assert runid3
        assert runid4
        assert runid5

        # run the command
        args = []
        opts = {}
        call_command('autocleanupvalidations', *args, **opts)

        ## reload from db because the validations have been changed.
        run1 = ValidationRun.objects.get(pk=runid1)
        run2 = ValidationRun.objects.get(pk=runid2)
        run3 = ValidationRun.objects.get(pk=runid3)
        run4 = ValidationRun.objects.get(pk=runid4)
        run5 = ValidationRun.objects.get(pk=runid5)

        ## with the last command call, the user should have been notified about most of our test validations
        ## but the validations should not have been deleted yet
        assert not run1.expiry_notified
        assert run2.expiry_notified
        assert run3.expiry_notified
        assert run4.expiry_notified
        assert run5.expiry_notified

        ## the validations may have been extended in the previous step, undo that to get them really deleted in the next call
        run1.last_extended = None
        run1.save()
        run2.last_extended = None
        run2.save()
        run3.last_extended = None
        run3.save()
        run4.last_extended = None
        run4.save()
        run5.last_extended = None
        run5.save()

        call_command('autocleanupvalidations', *args, **opts)

        ## the two expired validations should be have been deleted now
        ended_vals3 = ValidationRun.objects.filter(end_time__isnull=False).count()
        assert ended_vals + 3 == ended_vals3
