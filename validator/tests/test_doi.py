'''
Test DOI generation
'''

from datetime import timedelta
import logging
from os import path
import shutil

from django.contrib.auth import get_user_model
import pytest
User = get_user_model()

from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from validator.doi import get_doi_for_validation
from validator.models import DataVariable, Dataset, DatasetConfiguration, DatasetVersion, ValidationRun
from validator.validation import set_outfile, mkdir_if_not_exists
from validator.validation.globals import OUTPUT_FOLDER


# use zenodo test sandbox to avoid generating real dois
@override_settings(DOI_REGISTRATION_URL = "https://sandbox.zenodo.org/api/deposit/depositions")
@pytest.mark.long_running
class TestDOI(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters']

    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.user_data = {
            'username': 'chuck_norris',
            'password': 'roundhousekick',
            'email': 'norris@awst.at',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'organisation': 'Texas Rangers',
            'country' : 'US',
            'orcid' : '0000-0002-1825-0097',
            }
        self.testuser = User.objects.create_user(**self.user_data)

    def test_doi(self):
        infile = 'testdata/output_data/c3s_era5land.nc'

        ## generate test validation
        val = ValidationRun()
        val.start_time = timezone.now() - timedelta(days=1)
        val.end_time = timezone.now()
        val.user = self.testuser
        val.save()

        data_c = DatasetConfiguration()
        data_c.validation = val
        data_c.dataset = Dataset.objects.get(short_name='C3S')
        data_c.version = DatasetVersion.objects.get(short_name='C3S_V201812')
        data_c.variable = DataVariable.objects.get(short_name='C3S_sm')
        data_c.save()

        ref_c = DatasetConfiguration()
        ref_c.validation = val
        ref_c.dataset = Dataset.objects.get(short_name='ISMN')
        ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20191211')
        ref_c.variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')
        ref_c.save()

        val.reference_configuration = ref_c
        val.scaling_ref = ref_c
        val.save()

        ## set valid output file for validation
        run_dir = path.join(OUTPUT_FOLDER, str(val.id))
        mkdir_if_not_exists(run_dir)
        shutil.copy(infile, path.join(run_dir, 'results.nc'))
        set_outfile(val, run_dir)
        val.save()

        ## create a test doi on zenodo's sandbox service
        get_doi_for_validation(val)

        val = ValidationRun.objects.get(pk=val.id)
        self.__logger.debug(val.doi)
        assert val.doi
        firstdoi = val.doi

        ## try to upload the same data with the same title again - it should work but yield a different doi
        get_doi_for_validation(val)

        val = ValidationRun.objects.get(pk=val.id)
        self.__logger.debug(val.doi)
        assert val.doi
        assert val.doi != firstdoi
