'''
Test our custom django commands
'''

from datetime import datetime
import logging
from unittest.mock import patch

from dateutil.tz.tz import tzlocal
from django.core.management import call_command
from django.test import TestCase

from validator.models import Dataset
from validator.models import ValidationRun
from validator.tests.testutils import set_dataset_paths


# See https://stackoverflow.com/a/6513372/
class TestCommands(TestCase):

    fixtures = ['variables', 'versions', 'datasets', 'filters']

    __logger = logging.getLogger(__name__)

    def setUp(self):
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
        assert test_val.progress == -1

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
        with patch('builtins.input', side_effect=user_input): ## this mocks user input for the command
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
        with patch('builtins.input', side_effect=user_input): ## this mocks user input for the command
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
        with patch('builtins.input', side_effect=user_input): ## this mocks user input for the command
            # run the command
            call_command('setdatasetpaths', *args, **opts)

        # check that the datasets were changed correctly
        for counter, dataset in enumerate(Dataset.objects.all().order_by('id')):
            self.__logger.debug('checking path second time for ' + dataset.short_name)
            assert new_test_path2 in dataset.storage_path
            assert dataset.short_name in dataset.storage_path

