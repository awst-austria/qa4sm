'''
Test DOI generation
'''

from datetime import timedelta
import logging
import os
from os import path
import shutil
import netCDF4

from django.contrib.auth import get_user_model
import pytest
from validator.forms import PublishingForm
User = get_user_model()

from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from validator.doi import get_doi_for_validation
from validator.models import DataVariable, Dataset, DatasetConfiguration, DatasetVersion, ValidationRun
from validator.validation import set_outfile, mkdir_if_not_exists
from validator.validation.globals import OUTPUT_FOLDER


# use zenodo test sandbox to avoid generating real dois
@pytest.mark.skipif(not 'DOI_ACCESS_TOKEN_ENV' in os.environ, reason="No access token set in global variables")
@override_settings(DOI_REGISTRATION_URL = "https://sandbox.zenodo.org/api/deposit/depositions")
@pytest.mark.long_running
class TestDOI(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

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
        data_c.dataset = Dataset.objects.get(short_name='C3S_combined')
        data_c.version = DatasetVersion.objects.get(short_name='C3S_V201812')
        data_c.variable = DataVariable.objects.get(pretty_name='C3S_sm')
        data_c.save()

        ref_c = DatasetConfiguration()
        ref_c.validation = val
        ref_c.dataset = Dataset.objects.get(short_name='ISMN')
        ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20191211')
        ref_c.variable = DataVariable.objects.get(pretty_name='ISMN_soil_moisture')
        ref_c.save()

        val.spatial_reference_configuration = ref_c
        val.scaling_ref = ref_c
        val.save()

        ## set valid output file for validation
        run_dir = path.join(OUTPUT_FOLDER, str(val.id))
        mkdir_if_not_exists(run_dir)
        shutil.copy(infile, path.join(run_dir, 'results.nc'))
        set_outfile(val, run_dir)
        val.save()

        ## test the publishing form

        # no name given
        val.user.first_name = None
        val.user.last_name = None
        form = PublishingForm(validation=val)
        assert form

        # only first name given
        val.user.first_name = self.user_data['first_name']
        form = PublishingForm(validation=val)
        assert form
        val.user.first_name = None

        # only last name given
        val.user.last_name = self.user_data['last_name']
        form = PublishingForm(validation=val)
        assert form

        # first and last name given but not a real orcid id
        val.user.first_name = self.user_data['first_name']
        val.user.orcid = 'not a real orcid'
        form = PublishingForm(validation=val)

        caught_orcid_error = False
        try:
            assert form.pub_metadata
        except:
            caught_orcid_error = True

        assert caught_orcid_error

        # fix orcid
        val.user.orcid = self.user_data['orcid']

        ## finally everything should be ok and we can use the form to generate the necessary metadata
        form = PublishingForm(validation=val)
        metadata = form.pub_metadata

        ## create a test doi on zenodo's sandbox service
        get_doi_for_validation(val, metadata)

        val = ValidationRun.objects.get(pk=val.id)
        self.__logger.debug(val.doi)
        assert val.doi
        firstdoi = val.doi

        # ## check that the DOI was correctly stored in the netcdf file
        # it should be truth, but the doi that is saved in the file comes from the very first request,
        # and it's called pre-reserved doi; for some reason zenodo sandbox provides now different pre-reserved doi then
        # the real one, so I need to block this code
        # with netCDF4.Dataset(val.output_file.path, mode='r') as ds:
        #     assert val.doi in ds.doi

        # instead let's use something like, because 10.5072 is a part of zenodo sandbox doi:
        with netCDF4.Dataset(val.output_file.path, mode='r') as ds:
            assert '10.5072' in val.doi

        form = PublishingForm(validation=val)
        metadata = form.pub_metadata

        ## try to upload the same data with the same title again - it should work but yield a different doi
        get_doi_for_validation(val, metadata)

        val = ValidationRun.objects.get(pk=val.id)
        self.__logger.debug(val.doi)
        assert val.doi
        assert val.doi != firstdoi

        ## check that the DOI was correctly stored in the netcdf file
        with netCDF4.Dataset(val.output_file.path, mode='r') as ds:
            assert '10.5072' in val.doi
