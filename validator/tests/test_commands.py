'''
Test our custom django commands
'''

from datetime import datetime, timedelta
import logging
from tempfile import TemporaryDirectory
from unittest.mock import patch
import pandas as pd
import os

from dateutil.tz.tz import tzlocal
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from validator.models import Dataset
from validator.models import ValidationRun
from validator.tests.testutils import set_dataset_paths
from validator.validation import ISMN_LIST_FILE_NAME

from django.contrib.auth import get_user_model

User = get_user_model()


# See https://stackoverflow.com/a/6513372/
class TestCommands(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

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
        set_dataset_paths()

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
        assert test_val.progress == -100

    # def test_autocleanupvalidations(self):
    #
    #     ended_vals = ValidationRun.objects.filter(end_time__isnull=False).count()
    #
    #     ## unexpired validation
    #     run1 = ValidationRun()
    #     run1.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
    #     run1.end_time = timezone.now()
    #     run1.user = self.testuser
    #     run1.save()
    #     runid1 = run1.id
    #
    #     ## 20% of warning period has passed
    #     run2 = ValidationRun()
    #     run2.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
    #     run2.end_time = timezone.now() - timedelta(
    #         days=settings.VALIDATION_EXPIRY_DAYS - settings.VALIDATION_EXPIRY_WARNING_DAYS * 0.8)
    #     run2.user = self.testuser
    #     run2.save()
    #     runid2 = run2.id
    #
    #     ## 80% of warning period has passed
    #     run3 = ValidationRun()
    #     run3.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
    #     run3.end_time = timezone.now() - timedelta(
    #         days=settings.VALIDATION_EXPIRY_DAYS - settings.VALIDATION_EXPIRY_WARNING_DAYS * 0.2)
    #     run3.user = self.testuser
    #     run3.save()
    #     runid3 = run3.id
    #
    #     ## just expired validation
    #     run4 = ValidationRun()
    #     run4.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
    #     run4.end_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS)
    #     run4.user = self.testuser
    #     run4.save()
    #     runid4 = run4.id
    #
    #     ## long expired validation
    #     run5 = ValidationRun()
    #     run5.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
    #     run5.end_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 2)
    #     run5.user = self.testuser
    #     run5.save()
    #     runid5 = run5.id
    #
    #     # test what happens if there is no user assigned to a validation
    #     no_user_run = ValidationRun()
    #     no_user_run.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
    #     no_user_run.end_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS)
    #     no_user_run.user = None
    #     no_user_run.save()
    #     no_user_run_id = no_user_run.id
    #
    #     # test what happens if there is no user assigned to a validation, but validation has been published
    #     no_user_run_published = ValidationRun()
    #     no_user_run_published.start_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS * 4)
    #     no_user_run_published.end_time = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS)
    #     no_user_run_published.user = None
    #     no_user_run_published.doi = '10101/101.010'
    #     no_user_run_published.save()
    #     no_user_run_published_id = no_user_run_published.id
    #
    #     ended_vals2 = ValidationRun.objects.filter(end_time__isnull=False).count()
    #     assert ended_vals + 7 == ended_vals2
    #     assert runid1
    #     assert runid2
    #     assert runid3
    #     assert runid4
    #     assert runid5
    #     assert no_user_run_id
    #     assert no_user_run_published_id
    #
    #     # run the command
    #     args = []
    #     opts = {}
    #     call_command('autocleanupvalidations', *args, **opts)
    #
    #     ## reload from db because the validations have been changed.
    #     run1 = ValidationRun.objects.get(pk=runid1)
    #     run2 = ValidationRun.objects.get(pk=runid2)
    #     run3 = ValidationRun.objects.get(pk=runid3)
    #     run4 = ValidationRun.objects.get(pk=runid4)
    #     run5 = ValidationRun.objects.get(pk=runid5)
    #     non_user_val = ValidationRun.objects.filter(pk=no_user_run_id)
    #     no_user_run_published = ValidationRun.objects.get(pk=no_user_run_published_id)
    #
    #     ## with the last command call, the user should have been notified about most of our test validations
    #     ## but the validations should not have been deleted yet
    #     assert not run1.expiry_notified
    #     assert run2.expiry_notified
    #     assert run3.expiry_notified
    #     assert run4.expiry_notified
    #     assert run5.expiry_notified
    #     assert len(non_user_val) == 0  # there should be no validation anymore, because it was already removed
    #     assert not no_user_run_published.expiry_notified  # no notification sent
    #
    #     ## the validations may have been extended in the previous step, undo that to get them really deleted in the next call
    #     run1.last_extended = None
    #     run1.save()
    #     run2.last_extended = None
    #     run2.save()
    #     run3.last_extended = None
    #     run3.save()
    #     run4.last_extended = None
    #     run4.save()
    #     run5.last_extended = None
    #     run5.save()
    #
    #     call_command('autocleanupvalidations', *args, **opts)
    #
    #     ## the two expired validations should be have been deleted now
    #     ended_vals3 = ValidationRun.objects.filter(end_time__isnull=False).count()
    #     assert ended_vals + 4 == ended_vals3

    def test_setdatasetpaths(self):
        new_test_path = 'new_test_path/'
        new_test_path2 = 'another_test_path/'

        num_changed = 0
        # ensure that every second dataset has no storage path
        for counter, dataset in enumerate(Dataset.objects.all().order_by('id')):
            if counter % 2 == 0:
                dataset.storage_path = ''
                dataset.save()
                num_changed += 1
                self.__logger.debug('setting empty path for: ' + dataset.short_name)

        ## instruct the command to change only the empty paths, give no default path, and set a new path every time
        user_input = [
            'u',
            '',
        ]
        user_input.extend([new_test_path] * num_changed)
        args = []
        opts = {}
        with patch('builtins.input', side_effect=user_input):  ## this mocks user input for the command
            # run the command
            call_command('setdatasetpaths', *args, **opts)

        # check that the datasets were changed correctly
        for counter, dataset in enumerate(Dataset.objects.all().order_by('id')):
            self.__logger.debug('checking path for ' + dataset.short_name)
            if counter % 2 == 0:
                assert new_test_path in dataset.storage_path
            else:
                assert new_test_path not in dataset.storage_path

        ## second round of testing!

        ## instruct the command to change all paths, give a default path, and accept the suggestion every time
        user_input = [
            '',
            new_test_path2,
        ]
        user_input.extend([''] * Dataset.objects.count())
        args = []
        opts = {}
        with patch('builtins.input', side_effect=user_input):  ## this mocks user input for the command
            # run the command
            call_command('setdatasetpaths', *args, **opts)

        # check that the datasets were changed correctly
        for counter, dataset in enumerate(Dataset.objects.all().order_by('id')):
            self.__logger.debug('checking path second time for ' + dataset.short_name)
            assert new_test_path2 in dataset.storage_path

        ## third round of testing!

        ## instruct the command to change all paths, give no default path, and keep the existing path (default) every time
        user_input = [
            'a',
            '',
        ]
        user_input.extend([''] * Dataset.objects.count())
        args = []
        opts = {}
        with patch('builtins.input', side_effect=user_input):  ## this mocks user input for the command
            # run the command
            call_command('setdatasetpaths', *args, **opts)

        # check that the datasets were changed correctly
        for counter, dataset in enumerate(Dataset.objects.all().order_by('id')):
            self.__logger.debug('checking path second time for ' + dataset.short_name)
            assert new_test_path2 in dataset.storage_path
            assert dataset.short_name in dataset.storage_path

        with patch('builtins.input', side_effect=user_input):  ## this mocks user input for the command
            # run the command to list the paths
            call_command('getdatasetpaths', *args, **opts)

    def test_generateismnlist(self):
        args = []
        opts = {}
        call_command('generateismnlist', *args, **opts)
        out_path = os.path.join(Dataset.objects.get(short_name='ISMN').storage_path, ISMN_LIST_FILE_NAME)
        df = pd.read_csv(out_path)
        assert not df.empty
        os.remove(out_path)
        call_command('generateismnlist', *args, '-s', 'ISMN_V20191211')
        df = pd.read_csv(out_path)
        assert not df.empty

