from datetime import datetime
import os, errno
from time import sleep
from zipfile import ZipFile

from re import search as regex_search
from re import IGNORECASE  # @UnresolvedImport

from dateutil.tz import tzlocal
from django.test import TestCase
from django.test.utils import override_settings
import netCDF4
import pytest
from pytz import UTC

from django.contrib.auth import get_user_model
User = get_user_model()

import numpy as np
from validator.models import Dataset
from validator.models import DatasetConfiguration
from validator.models import DatasetVersion
from validator.models import ValidationRun
from validator.models import DataFilter
from validator.models import DataVariable
import validator.validation as val
from validator.validation import globals
from validator.validation.validation import _check_validation_configuration

'''
    Tests to check that the validation process really produces valid results ;-)
    This is just a stub that should be filled by TU Wien.
'''
@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestValidity(TestCase):

    fixtures = ['variables', 'versions', 'datasets', 'filters']

    # run before every test case
    def setUp(self):
        self.out_variables = ['gpi', 'lon', 'lat'] + list(globals.METRICS.keys())

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
        num_vars=-1
        with netCDF4.Dataset(run.output_file.path) as ds:
            ## check the metrics contained in the file
            for metric in self.out_variables:
                ## This gets all variables in the netcdf file that start with the name of the current metric
                metric_vars = ds.get_variables_by_attributes(name=lambda v: regex_search(r'^{}(_between|$)'.format(metric), v, IGNORECASE) is not None)

                ## check that all metrics have the same number of variables (depends on number of input datasets)
                if num_vars == -1:
                    num_vars = len(metric_vars)
                    assert num_vars > 0, 'No variables containing metric {}'.format(metric)
                else:
                    assert len(metric_vars) == num_vars, 'Number of variables for metric {} doesn\'t match number for other metrics'.format(metric)

                ## check the values of the variables for formal criteria (not empty, matches lenght of other variables, doesn't have too many NaNs)
                for m_var in metric_vars:
                    values = m_var[:]
                    assert values is not None

                    if length == -1:
                        length = len(values)
                        assert length > 0, 'Variable {} has no entries'.format(m_var.name)
                    else:
                        assert len(values) == length, 'Variable {} doesn\'t match other variables in length'.format(m_var.name)

                    nan_ratio = np.sum(np.isnan(values.data)) / float(len(values))
                    assert nan_ratio <= 0.35, 'Variable {} has too many NaNs. Ratio: {}'.format(metric, nan_ratio)

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
        run.start_time = datetime.now(tzlocal())
        run.user = self.testuser
        # set validation period
        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)
        run.save()

        data_c = DatasetConfiguration()
        data_c.validation = run
        data_c.dataset = Dataset.objects.get(short_name='C3S_combined')
        data_c.version = DatasetVersion.objects.get(short_name='C3S_V201812')
        data_c.variable = DataVariable.objects.get(pretty_name='C3S_sm')
        data_c.save() # object needs to be saved before m2m relationship can be used

        data_c.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        data_c.save()

        ref_c = DatasetConfiguration()
        ref_c.validation = run
        ref_c.dataset = Dataset.objects.get(short_name='ISMN')
        ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
        ref_c.variable = DataVariable.objects.get(pretty_name='ISMN_soil_moisture')
        ref_c.is_spatial_reference = True
        ref_c.is_temporal_reference = True
        ref_c.save()

        ref_c.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
        ref_c.save()

        run.spatial_reference_configuration = ref_c
        run.temporal_reference_configuration = ref_c
        run.save()

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


    def test_different_reference_configurations(self):
        run = ValidationRun()
        run.start_time = datetime.now(tzlocal())
        run.user = self.testuser
        # set validation period
        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)
        run.save()

        # add three different datasets
        data_1 = DatasetConfiguration()
        data_1.validation = run
        data_1.dataset = Dataset.objects.get(short_name='C3S_combined')
        data_1.version = DatasetVersion.objects.get(short_name='C3S_V201812')
        data_1.variable = DataVariable.objects.get(pretty_name='C3S_sm')
        data_1.save()  # object needs to be saved before m2m relationship can be used

        data_1.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        data_1.save()

        data_2 = DatasetConfiguration()
        data_2.validation = run
        data_2.dataset = Dataset.objects.get(short_name='ISMN')
        data_2.version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
        data_2.variable = DataVariable.objects.get(pretty_name='ISMN_soil_moisture')
        data_2.save()

        data_2.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
        data_2.save()

        data_3 = DatasetConfiguration()
        data_3.validation = run
        data_3.dataset = Dataset.objects.get(short_name='GLDAS')
        data_3.version = DatasetVersion.objects.get(short_name='GLDAS_NOAH025_3H_2_1')
        data_3.variable = DataVariable.objects.get(pretty_name='GLDAS_SoilMoi0_10cm_inst')
        data_3.save()  # object needs to be saved before m2m relationship can be used

        data_3.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        data_3.filters.add(DataFilter.objects.get(name='FIL_GLDAS_UNFROZEN'))
        data_3.save()

        run.spatial_reference_configuration = data_2
        run.temporal_reference_configuration = data_2
        run.save()

        # test case:
        # no dataset marked as spatial reference

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "No configuration is marked as spatial reference." in str(exc)

        # assign spatial reference to data_2
        data_2.is_spatial_reference = True
        data_2.save()

        # test case:
        # no dataset marked as temporal reference

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "No configuration is marked as temporal reference." in str(exc)

        # assign temporal reference to data_2:
        data_2.is_temporal_reference = True
        data_2.save()

        # test case - everything ok:
        # do not set scaling reference, as the default scaling reference method is none
        try:
            _check_validation_configuration(run)
        except Exception as exc:
            assert False, f"'_check_validation_configuration raised and exception {exc}'"

        # change spatial and temporal reference in the run, but do not change it in the dataset
        # test case:
        # 1 config set as spatial and temporal reference, but a different one assigned to the run
        run.spatial_reference_configuration = data_1
        run.temporal_reference_configuration = data_1
        run.save()
        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "Configuration is not marked as spatial reference." in str(exc)

        # assign spatial reference to the proper dataset, but do not remove it from the data_2:
        # test case:
        # more than one config set as spatial reference, but one of them is assigned to the run
        data_1.is_spatial_reference = True
        data_1.save()

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "More than one configuration is marked as spatial reference." in str(exc)

        # remove spatial reference info from data_1, but do not fix temporal
        # 1 config set as temporal reference, but a different one assigned to the run
        data_2.is_spatial_reference = False
        data_2.save()

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "Configuration is not marked as temporal reference." in str(exc)

        # assign temporal reference to data_1 but do not remove from data_2
        # test case:
        # more than one config set as temporal reference, but one of them assigned to the run
        data_1.is_temporal_reference = True
        data_1.save()

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "More than one configuration is marked as temporal reference." in str(exc)

        # remove temporal reference from data_2 -> again everything is ok
        data_2.is_temporal_reference = False
        data_2.save()

        try:
            _check_validation_configuration(run)
        except Exception as exc:
            assert False, f"'_check_validation_configuration raised and exception {exc}'"

        # change scaling method but do not set scaling reference:
        # test case:
        # scaling method set but scaling reference not
        run.scaling_method = ValidationRun.MEAN_STD
        run.save()

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "Scaling method is set, but scaling reference not." in str(exc)

        # set scaling reference in the run but do not assign it to any config
        # test case:
        # no config marked as scaing reference
        run.scaling_ref = data_1
        run.save()

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "No configuration is marked as scaling reference." in str(exc)

        # test case:
        # more than one config as scaling reference
        data_1.is_scaling_reference = True
        data_1.save()

        data_2.is_scaling_reference = True
        data_2.save()

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "More than one configuration is marked as scaling reference." in str(exc)

        # leaving data_2 as the scaling reference
        # test case:
        # a configuration marked as scaling reference but not the one that is assigned to the run
        data_1.is_scaling_reference = False
        data_1.save()

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "Configuration is not marked as scaling reference." in str(exc)

        # remove scaling method
        # test case:
        # scaling reference set in the run and assigned to a config, but method set to none
        run.scaling_method = ValidationRun.NO_SCALING
        run.save()

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "Scaling method is none, but scaling reference is set and a configuration is marked as reference." in str(exc)

        # remove scaling reference method but leave config with assigned information
        # test case:
        # scaling method and reference is not assigned to the run, but there is still a config marked as scaling
        # reference
        run.scaling_ref = None
        run.save()

        with pytest.raises(ValueError) as exc:
            _check_validation_configuration(run)
        assert "Scaling method is not set but at least one configuration is marked as reference." in str(exc)

        # test case - everything ok:
        # data 1 set as spatial, data 2 set as temporal, no scaling:
        data_1.is_temporal_reference = False
        data_1.save()

        data_2.is_scaling_reference = False
        data_2.is_temporal_reference = True
        data_2.save()

        run.temporal_reference_configuration = data_2
        run.save()

        try:
            _check_validation_configuration(run)
        except Exception as exc:
            assert False, f"'_check_validation_configuration raised and exception {exc}'"

        # test case - everything ok:
        # data 1 set as spatial, data 2 set as temporal and data 3 as the scaling reference
        run.scaling_method = ValidationRun.MEAN_STD
        run.scaling_ref = data_3
        run.save()

        data_3.is_scaling_reference = True
        data_3.save()

        try:
            _check_validation_configuration(run)
        except Exception as exc:
            assert False, f"'_check_validation_configuration raised and exception {exc}'"


