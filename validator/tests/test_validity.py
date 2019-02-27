from datetime import datetime
import os, errno
from time import sleep
from zipfile import ZipFile

from dateutil.tz import tzlocal
from django.conf import settings
from django.test import TestCase
import netCDF4
import pytest
from pytz import UTC

from django.contrib.auth import get_user_model
from validator.models import Dataset
from validator.models import DatasetVersion
from validator.models import DataVariable
User = get_user_model()

import numpy as np
from validator.models import ValidationRun
from validator.models.filter import DataFilter
import validator.validation as val

'''
    Tests to check that the validation process really produces valid results ;-)
'''
class TestValidity(TestCase):
    # run before every test case
    def setUp(self):
        settings.CELERY_TASK_ALWAYS_EAGER = True # run without parallelisation, everything in one process

        self.out_variables = ['gpi', 'lon', 'lat'] + list(val.METRICS.keys())

        self.user_data = {
            'username': 'testuser',
            'password': 'secret',
            'email': 'noreply@awst.at'
            }

        try:
            self.testuser = User.objects.get(username=self.user_data['username'])
        except User.DoesNotExist:
            self.testuser = User.objects.create_user(**self.user_data)

        try:
            os.makedirs(val.OUTPUT_FOLDER)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    ## helper method to check output of validation
    def generic_result_check(self, run):
        assert run is not None
        assert run.end_time is not None
        assert run.end_time > run.start_time
        assert run.total_points > 0
        assert run.error_points >= 0
        assert run.ok_points >= 0

        assert run.output_file

        outdir = os.path.dirname(run.output_file.path)

        ## check netcdf output
        length=-1
        with netCDF4.Dataset(run.output_file.path) as ds:
            for variable in self.out_variables:
                values = ds.variables[variable][:]
                assert values is not None

                if length == -1:
                    length = len(values)
                    assert length > 0, 'Variable {} has no entries'.format(variable)
                else:
                    assert len(values) == length, 'Variable {} doesn\'t match other variables in length'.format(variable)

                nan_ratio = np.sum(np.isnan(values.data)) / float(len(values))
                ## totally arbitrary ratio of not more than 35% NaNs in the metrics
                assert nan_ratio <= 0.35, 'Variable {} has too many NaNs. Ratio: {}'.format(variable, nan_ratio)

        # check zipfile of graphics
        zipfile = os.path.join(outdir, 'graphs.zip')
        assert os.path.isfile(zipfile)
        with ZipFile(zipfile, 'r') as myzip:
            assert myzip.testzip() is None
            for fname in myzip.namelist():
                data = myzip.read(fname)
                print(fname, len(data), repr(data[:10]))


    ## helper function to delete output of test validations, clean up after ourselves
    def delete_run(self, run):
        # let's see if the output file gets cleaned up when the model is deleted
        ncfile = run.output_file.path
        outdir = os.path.dirname(ncfile)
        assert os.path.isfile(ncfile)
        run.delete()
        assert not os.path.exists(outdir)

    @pytest.mark.filterwarnings("ignore:No results for gpi:UserWarning") # ignore pytesmo warnings about missing results
    @pytest.mark.long_running
    def test_validation_c3s_ismn(self):
        run = ValidationRun()
        run.user = self.testuser
        run.start_time = datetime.now(tzlocal())

        # set data set
        run.data_dataset = Dataset.objects.get(short_name='C3S')
        run.data_version = DatasetVersion.objects.get(short_name='C3S_V201706')
        run.data_variable = DataVariable.objects.get(short_name='C3S_sm')

        # set reference set
        run.ref_dataset = Dataset.objects.get(short_name='ISMN')
        run.ref_version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
        run.ref_variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')

        # set validation period
        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)

        run.save() ## need to save before adding filters because django m2m relations work that way

        run.data_filters.add(DataFilter.objects.get(name='FIL_C3S_FLAG_0'))
        run.data_filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        run.ref_filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
#         run.ref_filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
#         run.ref_filters.add(DataFilter.objects.get(name='FIL_GLDAS_UNFROZEN'))

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        ## wait until it's over (if necessary)
        finished_run = ValidationRun.objects.get(pk=run_id)
        timeout = 300 # seconds
        wait_time = 5 # seconds
        runtime = 0
        while(finished_run.end_time is None):
            assert runtime <= timeout, 'Validations are taking too long.'
            sleep(wait_time)
            runtime += wait_time

        ## TODO: check the results here

        self.generic_result_check(finished_run)
        self.delete_run(finished_run)
