from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
import pytest

from validator.models import CeleryTask
from validator.models import DataFilter
from validator.models import DataVariable
from validator.models import Dataset
from validator.models import DatasetVersion
from validator.models import Settings
from validator.models import ValidationRun


class TestModels(TestCase):

    def test_validation_run_str(self):
        run = ValidationRun()
        run_str = str(run)
        print(run_str)
        assert run_str is not None

    def test_validation_run_external_relations(self):
        run = ValidationRun()
        tasks = run.celery_tasks.all()
        assert tasks is not None

    def test_validation_run_output_dir_url(self):
        run = ValidationRun()
        assert run.output_dir_url() is None
        run.output_file = 'output/foobar.nc'
        assert run.output_dir_url() is not None

    def test_validation_run_clean(self):
        run = ValidationRun()

        ## default object should be valid
        run.clean()

        ## object with just a from date should be invalid
        run.interval_from = datetime(2000, 1, 1)
        with pytest.raises(ValidationError):
            run.clean()

        ## object with just a to start date should be invalid
        run.interval_from = None
        run.interval_to = datetime(2000, 1, 1)
        with pytest.raises(ValidationError):
            run.clean()

        ## object with from date after to date should be invalid
        run.interval_from = datetime(2001, 1, 1)
        with pytest.raises(ValidationError):
            run.clean()

        ## object with from date before to date should be valid
        run.interval_to = datetime(2005, 1, 1)
        run.clean()

    def test_data_filter_str(self):
        myfilter = DataFilter()
        filter_str = str(myfilter)
        print(filter_str)
        assert filter_str

        myfilter.id = 1337
        myfilter.name = 'FIL_DELICIOUS'
        myfilter.description = 'Filter for deliciousness'
        myfilter.help_text = 'Deliciousness is expressed by the d_flag'
        filter_str = str(myfilter)
        print(filter_str)
        assert filter_str

    def test_dataset_str(self):
        mydataset = Dataset()
        dataset_str = str(mydataset)
        print(dataset_str)
        assert dataset_str == ""

        mydataset.id = 1337
        mydataset.short_name = 'SUPERSAT'
        mydataset.pretty_name = 'Super satellite dataset'
        mydataset.help_text = 'Dataset from the super satellite - solves all problems!'
        mydataset.is_reference = True
        mydataset.source_reference = "<a href=\"http://tuwien.ac.at\">Click here!</a>"
        mydataset.citation = "<a href=\"http://tuwien.ac.at\">Click here!</a>"

        dataset_str = str(mydataset)
        print(dataset_str)
        assert dataset_str

    def test_version_str(self):
        mydatasetversion = DatasetVersion()
        dataset_str = str(mydatasetversion)
        print(dataset_str)
        assert dataset_str == ""

        mydatasetversion.id = 1337
        mydatasetversion.short_name = 'V2.0'
        mydatasetversion.pretty_name = 'Version 2.0'
        mydatasetversion.help_text = 'Version 2.0 has the latest foobar flag set to 0'

        version_str = str(mydatasetversion)
        print(version_str)
        assert version_str

    def test_variable_str(self):
        mydatavariable = DataVariable()
        dataset_str = str(mydatavariable)
        print(dataset_str)
        assert dataset_str == ""

        mydatavariable.id = 1337
        mydatavariable.short_name = 'SM'
        mydatavariable.pretty_name = 'SM'
        mydatavariable.help_text = 'Soil moisture in kg/m2'

        variable_str = str(mydatavariable)
        print(variable_str)
        assert variable_str

    def test_settings(self):
        settings = Settings.load()
        assert settings

        settings.save()

        # delete should have no effect
        settings.delete()
        settings = Settings.load()
        assert settings

    def test_celery_task_str(self):
        task = CeleryTask()
        task_str = str(task)
        print(task_str)
        assert task_str is not None
