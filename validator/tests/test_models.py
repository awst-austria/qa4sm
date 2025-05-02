from datetime import datetime
from datetime import timedelta
import logging

from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import now
import pytest

from validator.tests.testutils import set_dataset_paths
import os

import numpy as np
from validator.models import CeleryTask
from validator.models import DataFilter
from validator.models import DataVariable
from validator.models import Dataset
from validator.models import DatasetConfiguration
from validator.models import DatasetVersion
from validator.models import ParametrisedFilter
from validator.models import Settings
from validator.models import ValidationRun


class TestModels(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

    __logger = logging.getLogger(__name__)

    def test_user(self):
        user = User()
        user.clean()

        ## test valid orcids
        for testorcid in [
            "0000-0002-1825-0097",
            "0000-0002-9079-593X", ]:
            user.orcid = testorcid
            user.clean()
            assert user

        # test invalid orcids
        for testorcid in [
            "lah.",
            "0000-0002-1825-0097-5555",
            "0000-0002-9abc-593X", ]:
            with self.assertRaises(ValidationError):
                user.orcid = testorcid
                user.clean()

    def test_validation_configuration(self):
        run = ValidationRun()
        run.start_time = now()
        run.save()

        dc = DatasetConfiguration()
        dc.validation = run
        dc.dataset = Dataset.objects.get(pk=1)
        dc.version = DatasetVersion.objects.get(pk=1)
        dc.variable = DataVariable.objects.get(pk=1)

        dc.save()

        run.spatial_reference_configuration = dc
        run.scaling_ref = dc

        run.save()

        assert len(run.dataset_configurations.all()) == 1
        assert run.spatial_reference_configuration
        assert run.scaling_ref

    def test_testdata_integrity(self):
        """
        checks whether a submodule update is needed for the testdata repository
        """
        set_dataset_paths()
        for dataset in Dataset.objects.all():
            for version in dataset.versions.all():
                assert os.path.isdir(os.path.join(dataset.storage_path,
                                                  version.short_name)), (
                    "Folder not present for dataset version {}. Did you "
                    "remember to update the submodule?".format(
                    version))

    def test_dataset_configuration(self):
        dc = DatasetConfiguration()
        dc_str = str(dc)
        print(dc_str)
        assert dc_str is not None

    def test_ds_config_order(self):
        dataset_range = range(1, 6)
        run = ValidationRun()
        run.start_time = now()
        run.save()

        # create dataset configs in order of dataset ids
        for i in dataset_range:
            dc = DatasetConfiguration()
            dc.validation = run
            dc.dataset = Dataset.objects.get(pk=i)
            dc.version = dc.dataset.versions.first()
            dc.variable = dc.dataset.variables.first()
            dc.save()

        run.spatial_reference_configuration = dc
        run.scaling_ref = dc
        run.save()

        # check that we can get the order of dataset configs from the
        # validation run
        orderorder = run.get_datasetconfiguration_order()
        self.__logger.debug('Orig order {}'.format(orderorder))
        assert orderorder

        # check that they have the same order when using all()
        for i, dsc in enumerate(run.dataset_configurations.all(), 1):
            assert dsc.dataset.id == i
            assert dsc.id == orderorder[i - 1]

        # randomly change the order
        newworldorder = np.random.permutation(orderorder)
        self.__logger.debug('New order {}'.format(newworldorder))
        run.set_datasetconfiguration_order(newworldorder)

        # make sure the new order is used
        for i, dsc in enumerate(run.dataset_configurations.all(), 1):
            self.__logger.debug('current id {}'.format(dsc.id))
            assert dsc.id == newworldorder[i - 1]

    def test_validation_run_str(self):
        run = ValidationRun()
        run_str = str(run)
        print(run_str)
        assert run_str is not None

    def test_validation_run_external_relations(self):
        run = ValidationRun()
        tasks = run.celery_tasks.all()
        assert tasks is not None
        data_configs = run.dataset_configurations.all()
        assert data_configs is not None

    def test_validation_run_output_dir_url(self):
        run = ValidationRun()
        assert run.output_dir_url is None
        run.output_file = 'output/foobar.nc'
        assert run.output_dir_url is not None

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

        ## object with no spatial subsetting should be valid
        run.min_lat = None
        run.max_lat = None
        run.min_lon = None
        run.max_lon = None
        run.clean()

        ## spatial subsetting with only two coords should be invalid
        run.min_lat = -45.0
        run.max_lat = +45.0
        with pytest.raises(ValidationError):
            run.clean()

        ## spatial subsetting with four coords should be valid
        run.min_lon = -120.0
        run.max_lon = +120.0
        run.clean()

        ## climatology with moving average should be valid without time period
        run.anomalies = ValidationRun.MOVING_AVG_35_D
        run.clean()

        ## climatology without anomalies time period should be invalid
        run.anomalies = ValidationRun.CLIMATOLOGY
        with pytest.raises(ValidationError):
            run.clean()

        ## climatology with broken time period should be invalid
        run.anomalies_from = datetime(2005, 1, 1)
        run.anomalies_to = datetime(2000, 1, 1)
        with pytest.raises(ValidationError):
            run.clean()

        ## climatology with correct time period should be invalid
        run.anomalies_from = datetime(2000, 1, 1)
        run.anomalies_to = datetime(2005, 1, 1)
        run.clean()

        ## climatology with moving average should be invalid with time period
        run.anomalies = ValidationRun.MOVING_AVG_35_D
        with pytest.raises(ValidationError):
            run.clean()

    def test_validation_run_expiry(self):
        assert settings.VALIDATION_EXPIRY_DAYS >= 1
        assert settings.VALIDATION_EXPIRY_WARNING_DAYS >= 1
        assert (settings.VALIDATION_EXPIRY_WARNING_DAYS <
                settings.VALIDATION_EXPIRY_DAYS)

        ## while the validation is running, we don't have an expiry date
        run = ValidationRun()
        assert run.expiry_date is None
        assert not run.is_expired
        assert not run.is_near_expiry

        ## once the validation has finished, it can expire
        run.end_time = timezone.now()
        assert run.expiry_date == (run.end_time + timedelta(
            days=settings.VALIDATION_EXPIRY_DAYS))
        assert not run.is_expired
        assert not run.is_near_expiry

        ## move us to the warning period
        run.end_time = timezone.now() - timedelta(
            days=settings.VALIDATION_EXPIRY_DAYS -
                 settings.VALIDATION_EXPIRY_WARNING_DAYS + 1)
        assert not run.is_expired
        assert run.is_near_expiry

        ## make the validation expire
        run.end_time = timezone.now() - timedelta(
            days=settings.VALIDATION_EXPIRY_DAYS + 1)
        assert run.is_expired
        assert run.is_near_expiry

        ## once the validation has been extended, it expires based on the
        # extension date
        run.end_time = timezone.now() - timedelta(days=7)
        run.last_extended = timezone.now()
        assert run.expiry_date == (run.last_extended + timedelta(
            days=settings.VALIDATION_EXPIRY_DAYS))

        ## move us to the warning period
        run.last_extended = timezone.now() - timedelta(
            days=settings.VALIDATION_EXPIRY_DAYS -
                 settings.VALIDATION_EXPIRY_WARNING_DAYS + 1)
        assert not run.is_expired
        assert run.is_near_expiry

        ## make the validation expire
        run.last_extended = timezone.now() - timedelta(
            days=settings.VALIDATION_EXPIRY_DAYS + 1)
        assert run.is_expired
        assert run.is_near_expiry

        ## if a validation is archived, it does not expire
        run.archive(commit=False)
        assert run.is_archived
        assert run.expiry_date is None
        assert not run.is_expired
        assert not run.is_near_expiry

        ## if validation is un-archived, it should be extended automatically
        run.archive(unarchive=True, commit=False)
        assert not run.is_archived
        assert not run.expiry_notified
        assert run.last_extended is not None
        assert not run.is_expired
        assert not run.is_near_expiry

        ## extend again, for good measure
        run.extend_lifespan(commit=False)
        assert not run.expiry_notified
        assert run.last_extended is not None
        assert not run.is_expired
        assert not run.is_near_expiry

    def test_deleteable(self):
        run = ValidationRun()
        assert run.is_unpublished

        run.doi = '10.1000/182'
        assert not run.is_unpublished

        run.doi = ''
        assert run.is_unpublished

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
        mydataset.help_text = ('Dataset from the super satellite - solves all '
                               'problems!')
        mydataset.is_reference = True
        mydataset.source_reference = ("<a href=\"http://tuwien.ac.at\">Click "
                                      "here!</a>")
        mydataset.citation = "<a href=\"http://tuwien.ac.at\">Click here!</a>"

        dataset_str = str(mydataset)
        print(dataset_str)
        assert dataset_str

    def test_dataset_resolution(self):
        mydataset = Dataset()
        assert mydataset.resolution_in_m == 30e3
        mydataset.resolution = {"value": 0.25, "unit": "deg"}
        assert mydataset.resolution_in_m == 25e3
        mydataset.resolution = {"value": 0.25, "unit": "km"}
        assert mydataset.resolution_in_m == 250

    def test_version_str(self):
        mydatasetversion = DatasetVersion()
        dataset_str = str(mydatasetversion)
        print(dataset_str)
        assert dataset_str == ""

        mydatasetversion.id = 1337
        mydatasetversion.short_name = 'V2.0'
        mydatasetversion.pretty_name = 'Version 2.0'
        mydatasetversion.help_text = ('Version 2.0 has the latest foobar flag'
                                      ' set to 0')

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

        s = str(settings)
        self.__logger.info(s)

    def test_celery_task(self):
        task = CeleryTask()
        task_string = str(task)
        self.__logger.debug(task_string)
        assert task_string

    def test_parametrised_filter(self):
        pfilter = ParametrisedFilter()
        pfstring = str(pfilter)
        assert pfstring

        myfilter = DataFilter()
        myfilter.id = 1337
        myfilter.name = 'FIL_ISMN_NETWORKS'
        myfilter.description = 'Pick ISMN networks:'
        myfilter.help_text = 'Pick them now!'
        myfilter.parameterised = True
        myfilter.dialog_name = 'ismn_dialog'

        pfilter.filter = myfilter
        pfilter.parameters = "AMMA-CATCH,CARBOAFRICA"
        pfstring = str(pfilter)
        assert pfstring

        pfilter.clean()

        clean_except = False
        try:
            pfilter.filter.parameterised = False
            pfilter.clean()
        except ValidationError:
            clean_except = True

        assert clean_except
