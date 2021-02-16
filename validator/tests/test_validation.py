from datetime import datetime
import fnmatch
import logging
from os import path
import os, errno
from re import IGNORECASE  # @UnresolvedImport
from re import search as regex_search
import shutil
import time
from zipfile import ZipFile

from dateutil.tz import tzlocal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()
from django.test import TestCase
from django.test.utils import override_settings
import netCDF4
import pytest
from pytz import UTC

import numpy as np
import pandas as pd
from django.conf import settings
from validator.models import DataFilter
from validator.models import DataVariable
from validator.models import Dataset
from validator.models import DatasetConfiguration
from validator.models import DatasetVersion
from validator.models import ParametrisedFilter
from validator.models import ValidationRun
from validator.models import CopiedValidations
from validator.tests.testutils import set_dataset_paths
from validator.validation import globals
import validator.validation as val
from validator.validation.batches import _geographic_subsetting
from validator.validation.globals import METRICS, TC_METRICS
from validator.validation.globals import OUTPUT_FOLDER
from validator.views.validation import _compare_validation_runs
from validator.views.results import _copy_validationrun
from django.shortcuts import get_object_or_404
from validator.tests.auxiliary_functions import generate_default_validation, generate_default_validation_triple_coll



@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestValidation(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters']
    austria_coordinates = [48.1, 15., 48.4, 16.]

    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.metrics = ['gpi', 'lon', 'lat'] + list(METRICS.keys())
        self.tcol_metrics = list(TC_METRICS.keys())

        self.user_data = {
            'username': 'testuser',
            'password': 'secret',
            'email': 'noreply@awst.at'
        }
        self.user2_data = {
            'username': 'bojack',
            'password': 'horseman',
            'email': 'bojack@awst.at'
        }

        try:
            self.testuser = User.objects.get(username=self.user_data['username'])
            self.testuser2 = User.objects.get(username=self.user2_data['username'])
        except User.DoesNotExist:
            self.testuser = User.objects.create_user(**self.user_data)
            self.testuser2 = User.objects.create_user(**self.user2_data)

        try:
            os.makedirs(val.OUTPUT_FOLDER)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        set_dataset_paths()

    def generate_default_validation(self):
        run = ValidationRun()
        run.start_time = datetime.now(tzlocal())
        run.save()

        data_c = DatasetConfiguration()
        data_c.validation = run
        data_c.dataset = Dataset.objects.get(short_name='CGLS_CSAR_SSM1km')
        data_c.version = DatasetVersion.objects.get(short_name='CGLS_CSAR_SSM1km_V1_1')
        data_c.variable = DataVariable.objects.get(short_name='S1_SSM')
        data_c.save()

        ref_c = DatasetConfiguration()
        ref_c.validation = run
        ref_c.dataset = Dataset.objects.get(short_name='ISMN')
        ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20191211')
        ref_c.variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')
        ref_c.save()

        run.reference_configuration = ref_c
        run.scaling_ref = ref_c

        run.save()

        return run

    def generate_default_validation_triple_coll(self):
        run = ValidationRun()
        run.start_time = datetime.now(tzlocal())
        run.save()

        data_c = DatasetConfiguration()
        data_c.validation = run
        data_c.dataset = Dataset.objects.get(short_name='CGLS_CSAR_SSM1km')
        data_c.version = DatasetVersion.objects.get(short_name='CGLS_CSAR_SSM1km_V1_1')
        data_c.variable = DataVariable.objects.get(short_name='S1_SSM')
        data_c.save()

        other_data_c = DatasetConfiguration()
        other_data_c.validation = run
        other_data_c.dataset = Dataset.objects.get(short_name='SMOS')
        other_data_c.version = DatasetVersion.objects.get(short_name='SMOS_105_ASC')
        other_data_c.variable = DataVariable.objects.get(short_name='SMOS_sm')
        other_data_c.save()

        ref_c = DatasetConfiguration()
        ref_c.validation = run
        ref_c.dataset = Dataset.objects.get(short_name='ISMN')
        ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20191211')
        ref_c.variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')
        ref_c.save()
        
        run.reference_configuration = ref_c
        run.scaling_ref = ref_c
        run.tcol = True
        run.save()
        
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='WEGENERNET',\
                                     dataset_config=run.reference_configuration)
        pfilter.save()
        # add filterring according to depth_range so that data in wegnernet is found:
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0, 0.2", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()

        return run

    ## check output of validation
    def check_results(self, run, is_tcol_run=False):
        assert run is not None
        assert run.end_time is not None
        assert run.end_time > run.start_time
        assert run.total_points > 0
        assert run.error_points >= 0
        assert run.ok_points >= 0

        assert run.output_file

        outdir = os.path.dirname(run.output_file.path)

        n_datasets = run.dataset_configurations.count()

        tcol_metrics = self.tcol_metrics if is_tcol_run else []
        pair_metrics = [m for m in list(METRICS.keys()) if m.lower() != 'n_obs']
        comm_metrics = [m for m in self.metrics if m not in pair_metrics]

        ## check netcdf output
        length = -1
        num_vars = -1
        with netCDF4.Dataset(run.output_file.path, mode='r') as ds:
            assert ds.qa4sm_version == settings.APP_VERSION
            assert ds.qa4sm_env_url == settings.ENV_FILE_URL_TEMPLATE.format(settings.APP_VERSION)
            assert str(run.id) in ds.url
            assert settings.SITE_URL in ds.url

            ## check the metrics contained in the file
            for metric in self.metrics + tcol_metrics:  # we dont test lon, lat, time etc.
                ## This gets all variables in the netcdf file that start with the name of the current metric
                if metric in tcol_metrics:
                    metric_vars = ds.get_variables_by_attributes(
                        name=lambda v: regex_search(r'^{}(.+?_between|$)'.format(metric), v, IGNORECASE) is not None)
                else:
                    metric_vars = ds.get_variables_by_attributes(
                        name=lambda v: regex_search(r'^{}(_between|$)'.format(metric), v, IGNORECASE) is not None)

                self.__logger.debug(f'Metric variables for metric {metric} are {[m.name for m in metric_vars]}')

                ## check that all metrics have the same number of variables (depends on number of input datasets)
                if metric in comm_metrics:
                    num_vars = 1
                elif metric in pair_metrics:
                    num_vars = n_datasets - 1
                elif metric in tcol_metrics:
                    num_vars = n_datasets - 1
                else:
                    raise ValueError(f"Unknown metric {metric}")

                assert len(metric_vars) > 0, 'No variables containing metric {}'.format(metric)
                assert len(
                    metric_vars) == num_vars, 'Number of variables for metric {} doesn\'t match number for other metrics'.format(
                    metric)

                ## check the values of the variables for formal criteria (not empty, matches lenght of other variables, doesn't have too many NaNs)
                for m_var in metric_vars:
                    values = m_var[:]
                    assert values is not None

                    if length == -1:
                        length = len(values)
                        assert length > 0, 'Variable {} has no entries'.format(m_var.name)
                    else:
                        assert len(values) == length, 'Variable {} doesn\'t match other variables in length'.format(
                            m_var.name)
                    self.__logger.debug(f'Length {m_var.name} are {length}')

                    nan_ratio = np.sum(np.isnan(values.data)) / float(len(values))
                    assert nan_ratio <= 0.35, 'Variable {} has too many NaNs. Ratio: {}'.format(metric, nan_ratio)

            if (run.interval_from is None):
                assert ds.val_interval_from == "N/A", 'Wrong validation config attribute. [interval_from]'
            else:
                assert ds.val_interval_from == run.interval_from.strftime(
                    '%Y-%m-%d %H:%M'), 'Wrong validation config attribute. [interval_from]'

            if (run.interval_to is None):
                assert ds.val_interval_to == "N/A", 'Wrong validation config attribute. [interval_to]'
            else:
                assert ds.val_interval_to == run.interval_to.strftime(
                    '%Y-%m-%d %H:%M'), 'Wrong validation config attribute. [interval_to]'

            assert run.anomalies == ds.val_anomalies, 'Wrong validation config attribute. [anomalies]'
            if (run.anomalies == ValidationRun.CLIMATOLOGY):
                assert ds.val_anomalies_from == run.anomalies_from.strftime(
                    '%Y-%m-%d %H:%M'), 'Anomalies baseline start wrong'
                assert ds.val_anomalies_to == run.anomalies_to.strftime(
                    '%Y-%m-%d %H:%M'), 'Anomalies baseline end wrong'
            else:
                assert 'val_anomalies_from' not in ds.ncattrs(), 'Anomalies baseline period start should not be set'
                assert 'val_anomalies_to' not in ds.ncattrs(), 'Anomalies baseline period end should not be set'

            if all(x is not None for x in [run.min_lat, run.min_lon, run.max_lat, run.max_lon]):
                assert ds.val_spatial_subset == "[{}, {}, {}, {}]".format(run.min_lat, run.min_lon, run.max_lat,
                                                                          run.max_lon)

            i = 0
            for dataset_config in run.dataset_configurations.all():

                if ((run.reference_configuration) and
                        (dataset_config.id == run.reference_configuration.id)):
                    d_index = 0
                else:
                    i += 1
                    d_index = i

                ds_name = 'val_dc_dataset' + str(d_index)
                stored_dataset = ds.getncattr(ds_name)
                stored_version = ds.getncattr('val_dc_version' + str(d_index))
                stored_variable = ds.getncattr('val_dc_variable' + str(d_index))
                stored_filters = ds.getncattr('val_dc_filters' + str(d_index))

                stored_dataset_pretty = ds.getncattr('val_dc_dataset_pretty_name' + str(d_index))
                stored_version_pretty = ds.getncattr('val_dc_version_pretty_name' + str(d_index))
                stored_variable_pretty = ds.getncattr('val_dc_variable_pretty_name' + str(d_index))

                # check dataset, version, variable
                assert stored_dataset == dataset_config.dataset.short_name, 'Wrong dataset config attribute. [dataset]'
                assert stored_version == dataset_config.version.short_name, 'Wrong dataset config attribute. [version]'
                assert stored_variable == dataset_config.variable.short_name, 'Wrong dataset config attribute. [variable]'

                assert stored_dataset_pretty == dataset_config.dataset.pretty_name, 'Wrong dataset config attribute. [dataset pretty name]'
                assert stored_version_pretty == dataset_config.version.pretty_name, 'Wrong dataset config attribute. [version pretty name]'
                assert stored_variable_pretty == dataset_config.variable.pretty_name, 'Wrong dataset config attribute. [variable pretty name]'

                # check filters
                if not dataset_config.filters.all() and not dataset_config.parametrisedfilter_set.all():
                    assert stored_filters == 'N/A', 'Wrong dataset config filters (should be none)'
                else:
                    assert stored_filters, 'Wrong dataset config filters (shouldn\'t be empty)'
                    for fil in dataset_config.filters.all():
                        assert fil.description in stored_filters, 'Wrong dataset config filters'
                    for pfil in dataset_config.parametrisedfilter_set.all():
                        assert pfil.filter.description in stored_filters, 'Wrong dataset config parametrised filters'
                        assert pfil.parameters in stored_filters, 'Wrong dataset config parametrised filters: no parameters'

                # check reference
                if dataset_config.id == run.reference_configuration.id:
                    assert ds.val_ref == ds_name, 'Wrong validation config attribute. [reference_configuration]'

                if dataset_config.id == run.scaling_ref.id:
                    assert ds.val_scaling_ref == ds_name, 'Wrong validation config attribute. [scaling_ref]'

            assert ds.val_scaling_method == run.scaling_method, ' Wrong validation config attribute. [scaling_method]'

        # check zipfile of graphics
        zipfile = os.path.join(outdir, 'graphs.zip')
        assert os.path.isfile(zipfile)
        with ZipFile(zipfile, 'r') as myzip:
            assert myzip.testzip() is None

        # check diagrams
        boxplot_pngs = [x for x in os.listdir(outdir) if fnmatch.fnmatch(x, 'boxplot*.png')]
        self.__logger.debug(boxplot_pngs)
        assert len(boxplot_pngs) == len(globals.METRICS.keys()) + (len(tcol_metrics) * (n_datasets - 1))

        overview_pngs = [x for x in os.listdir(outdir) if fnmatch.fnmatch(x, 'overview*.png')]
        self.__logger.debug(overview_pngs)
        # n_obs + one for each data set for all other metrics
        assert len(overview_pngs) == 1 + ((len(pair_metrics) + len(tcol_metrics)) * (n_datasets - 1))

    ## delete output of test validations, clean up after ourselves
    def delete_run(self, run):
        # let's see if the output file gets cleaned up when the model is deleted

        ncfile = run.output_file.path
        outdir = os.path.dirname(ncfile)
        assert os.path.isfile(ncfile)
        run.delete()
        assert not os.path.exists(outdir)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning")  # ignore pytesmo warnings about missing results
    @pytest.mark.filterwarnings(
        "ignore:read_ts is deprecated, please use read instead:DeprecationWarning")  # ignore pytesmo warnings about read_ts
    def test_validation(self):
        run = generate_default_validation()
        run.user = self.testuser

        #run.scaling_ref = ValidationRun.SCALE_REF
        run.scaling_method = ValidationRun.BETA_SCALING # cdf matching

        run.interval_from = datetime(2014, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)

        run.save()

        for config in run.dataset_configurations.all():
            if config == run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))

            config.save()

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='WEGENERNET',\
                                     dataset_config=run.reference_configuration)
        pfilter.save()
        # add filterring according to depth_range so that data in wegnernet is found:
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0, 0.2", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)
        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run.total_points == 4 # 4 stations in wegenernet
        assert new_run.error_points == 0
        assert new_run.ok_points == 4

        self.check_results(new_run)
        self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning")  # ignore pytesmo warnings about missing results
    @pytest.mark.filterwarnings(
        "ignore:read_ts is deprecated, please use read instead:DeprecationWarning")  # ignore pytesmo warnings about read_ts
    def test_validation_tcol(self):
        run = generate_default_validation_triple_coll()
        run.user = self.testuser

        # run.scaling_ref = ValidationRun.SCALE_REF
        run.scaling_method = ValidationRun.BETA_SCALING  # cdf matching

        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)

        run.save()

        for config in run.dataset_configurations.all():
            if config == run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
            else:
                if config.dataset.short_name == 'SMOS':
                    config.filters.add(DataFilter.objects.get(name='FIL_SMOS_UNFROZEN'))
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

            config.save()

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='WEGENERNET',\
                                     dataset_config=run.reference_configuration)
        pfilter.save()
        # add filterring according to depth_range so that data in wegnernet is found:
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0, 0.2", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()


        run_id = run.id

        ## run the validation
        val.run_validation(run_id)
        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run.total_points == 4 # 4 stations in wegenernet
        assert new_run.error_points == 0
        assert new_run.ok_points == 4

        self.check_results(new_run, is_tcol_run=True)
        self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning")  # ignore pytesmo warnings about missing results
    @pytest.mark.filterwarnings(
        "ignore:read_ts is deprecated, please use read instead:DeprecationWarning")  # ignore pytesmo warnings about read_ts
    def test_validation_empty_network(self):
        run = generate_default_validation()
        run.user = self.testuser

        #run.scaling_ref = ValidationRun.SCALE_REF
        run.scaling_method = ValidationRun.BETA_SCALING # cdf matching 

        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)

        run.save()

        for config in run.dataset_configurations.all():
            if config == run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
            else:
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

            config.save()

        # add filterring according to depth_range with values which cause that there is no points anymore:
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="98,99", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run.total_points == 0
        assert new_run.error_points == 0
        assert new_run.ok_points == 0

    @pytest.mark.long_running
    def test_validation_anomalies_moving_avg(self):
        run = self.generate_default_validation()
        run.user = self.testuser
        run.anomalies = ValidationRun.MOVING_AVG_35_D
        run.save()

        run.reference_configuration.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        run.reference_configuration.save()
        for config in run.dataset_configurations.all():
            if config != run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            config.save()

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='WEGENERNET',\
                                     dataset_config=run.reference_configuration)
        pfilter.save()
        # add filterring according to depth_range so that data in wegnernet is found:
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0, 0.2", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run
        assert new_run.total_points == 4
        assert new_run.error_points == 0
        assert new_run.ok_points == 4
        self.check_results(new_run)
        self.delete_run(new_run)

    @pytest.mark.filterwarnings("ignore:No results for gpi:UserWarning")
    @pytest.mark.filterwarnings("ignore:No data for:UserWarning")
    @pytest.mark.long_running
    @pytest.mark.skip(reason="Currently no model in HR instance")
    def test_validation_model_ref(self):
        # todo: when there is a model refernece dataset available add this test
        return

    @pytest.mark.long_running
    def test_validation_smos_ref(self):
        run = self.generate_default_validation()
        run.user = self.testuser

        run.reference_configuration.dataset = Dataset.objects.get(short_name=globals.SMOS)
        run.reference_configuration.version = DatasetVersion.objects.get(short_name=globals.SMOS_105_ASC)
        run.reference_configuration.variable = DataVariable.objects.get(short_name=globals.SMOS_sm)
        run.reference_configuration.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

        run.reference_configuration.save()

        run.interval_from = datetime(2016, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2017, 1, 1, tzinfo=UTC)
        run.min_lat = self.austria_coordinates[0]
        run.min_lon = self.austria_coordinates[1]
        run.max_lat = self.austria_coordinates[2]
        run.max_lon = self.austria_coordinates[3]

        run.save()

        for config in run.dataset_configurations.all():
            if config != run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            config.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)
        print(new_run)
        assert new_run

        assert new_run.total_points == 4, "Number of gpis is off"
        assert new_run.error_points == 0, "Too many error gpis"
        assert new_run.ok_points == 4, "OK points are off"
        self.check_results(new_run)
        self.delete_run(new_run)

    @pytest.mark.long_running
    def test_validation_anomalies_climatology(self):
        run = generate_default_validation()
        run.user = self.testuser
        run.anomalies = ValidationRun.CLIMATOLOGY
        # make sure there is data for the climatology time period!
        run.anomalies_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.anomalies_to = datetime(2018, 12, 31, 23, 59, 59)
        run.save()

        run.reference_configuration.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        run.reference_configuration.save()
        for config in run.dataset_configurations.all():
            if config != run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            config.save()


        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='WEGENERNET',\
                                     dataset_config=run.reference_configuration)
        pfilter.save()
        # add filterring according to depth_range so that data in wegnernet is found:
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0, 0.2", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run
        assert new_run.total_points == 4
        assert new_run.error_points == 0
        assert new_run.ok_points == 4
        self.check_results(new_run)
        self.delete_run(new_run)
    
    @pytest.mark.long_running
    def test_validation_spatial_subsetting(self):
        run = generate_default_validation()
        run.user = self.testuser

        # austria bounding box
        run.min_lat = 46.4318173285 # ll
        run.min_lon = 9.47996951665  # ll
        run.max_lat = 49.0390742051  # ur
        run.max_lon = 16.9796667823  # ur

        run.save()

        run.reference_configuration.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        run.reference_configuration.save()
        for config in run.dataset_configurations.all():
            if config != run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            config.save()

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='WEGENERNET',\
                                     dataset_config=run.reference_configuration)
        pfilter.save()
        # add filterring according to depth_range so that data in wegnernet is found:
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0, 0.2", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run
        assert new_run.total_points == 4
        assert new_run.error_points == 0
        assert new_run.ok_points == 4
        self.check_results(new_run)
        self.delete_run(new_run)

    def test_errors(self):
        dataset = Dataset()
        dataset.short_name = 'gibtsnicht'
        version = DatasetVersion()
        version.short_name = '-3.14'

        ## readers
        with pytest.raises(ValueError):
            no_reader = val.create_reader(dataset, version)
            print(no_reader)

        ## save config
        validation_run = ValidationRun()
        val.save_validation_config(validation_run)

    def test_readers(self):
        start_time = time.time()

        datasets = Dataset.objects.all()
        print(datasets)
        for dataset in datasets:
            vs = dataset.versions.all()
            for version in vs:
                print("Testing {} version {}".format(dataset, version))

                reader = val.create_reader(dataset, version)

                assert reader is not None
                if dataset.short_name == val.globals.ISMN:
                    data = reader.read_ts(0)
                else:
                    data = reader.read_ts(15.8, 47.9) ## austriia
                print(data)

                assert data is not None
                assert isinstance(data, pd.DataFrame)

        print("Test duration: {}".format(time.time() - start_time))

    # minimal test of filtering, quicker than the full test below
    def test_setup_filtering_min(self):
        dataset = Dataset.objects.get(short_name='ISMN')
        version = DatasetVersion.objects.get(short_name='ISMN_V20191211')
        variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')
        reader = val.create_reader(dataset, version)

        no_msk_reader = val.setup_filtering(reader, None, None, dataset, variable)
        assert no_msk_reader is not None
        data = no_msk_reader.read_ts(0)
        assert data is not None
        assert isinstance(data, pd.DataFrame)
        assert len(data.index) > 1
        assert not data[variable.pretty_name].empty

        data_filters = [
            DataFilter.objects.get(name="FIL_ALL_VALID_RANGE"),
            DataFilter.objects.get(name="FIL_ISMN_GOOD"),
        ]
        param_filters = [
            ParametrisedFilter(filter = DataFilter.objects.get(name="FIL_ISMN_NETWORKS"), parameters = "  COSMOS , WEGENERNET "),
            ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0,0.2")
            ]

        msk_reader = val.setup_filtering(reader, data_filters, param_filters, dataset, variable)

        assert msk_reader is not None
        data = msk_reader.read_ts(0)
        assert data is not None
        assert isinstance(data, pd.DataFrame)
        assert len(data.index) > 1
        assert not data[variable.pretty_name].empty
        assert not np.any(data[variable.pretty_name].values < 0)
        assert not np.any(data[variable.pretty_name].values > 100)

    # test potential depth ranges errors
    def test_depth_range_filtering_errors(self):
        # perparing Validation run for ISMN
        run = ValidationRun()
        run.start_time = datetime.now(tzlocal())
        run.save()

        dataset = Dataset.objects.get(short_name='ISMN')
        version = dataset.versions.all()[0]

        ref_c = DatasetConfiguration()
        ref_c.validation = run
        ref_c.dataset = dataset
        ref_c.version = version
        ref_c.variable = dataset.variables.first()
        ref_c.save()
        run.reference_configuration = ref_c
        run.save()

        # adding filters where depth_to is smaller than depth_from
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.2,0.1", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()

        with pytest.raises(ValueError, match=r".*than.*"):
            val.create_jobs(run)

        ParametrisedFilter.objects.all().delete()

        # adding filters with negative values
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="-0.05,0.1", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()

        with pytest.raises(ValueError, match=r".*negative.*"):
            val.create_jobs(run)

        ParametrisedFilter.objects.all().delete()

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="-0.05,-0.1", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()

        with pytest.raises(ValueError, match=r".*negative.*"):
            val.create_jobs(run)

        ParametrisedFilter.objects.all().delete()

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.05,-0.1", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()

        with pytest.raises(ValueError, match=r".*negative.*"):
            val.create_jobs(run)

    # test all combinations of datasets, versions, variables, and filters
    @pytest.mark.long_running
    def test_setup_filtering_max(self):
        start_time = time.time()

        for dataset in Dataset.objects.all():
            self.__logger.info(dataset.pretty_name)
            vs = dataset.versions.all()
            va = dataset.variables.all()
            fils = dataset.filters.all()

            for version in vs:
                reader = val.create_reader(dataset, version)
                for variable in va:
                    for data_filter in fils:
                        self.__logger.debug(
                            "Testing {} version {} variable {} filter {}".format(dataset, version, variable,
                                                                                 data_filter.name))
                        if data_filter.parameterised:
                            pfilter = ParametrisedFilter(filter=data_filter, parameters=data_filter.default_parameter)
                            msk_reader = val.setup_filtering(reader, [], [pfilter], dataset, variable)
                        else:
                            msk_reader = val.setup_filtering(reader, [data_filter], [], dataset, variable)

                        assert msk_reader is not None
                        if dataset.short_name == val.globals.ISMN:
                            data = msk_reader.read_ts(0)
                        else:
                            data = msk_reader.read_ts(15.8, 48.3) ### austriia

                        assert data is not None
                        assert isinstance(data, pd.DataFrame)
                        assert len(data.index) > 1
                        assert not data[variable.pretty_name].empty

        print("Test duration: {}".format(time.time() - start_time))

    def _check_jobs(self, total_points, jobs):
        assert jobs
        assert total_points > 0
        assert len(jobs) > 0
        gpisum = 0
        for job in jobs:
            assert len(job) == 3
            if np.isscalar(job[0]):
                assert np.isscalar(job[1])
                assert np.isscalar(job[2])
                gpisum += 1
            else:
                numgpis = len(job[0])
                gpisum += numgpis
                assert numgpis > 0
                assert len(job[1]) == numgpis
                assert len(job[2]) == numgpis

        assert total_points == gpisum

    def test_create_jobs(self):
        for dataset in Dataset.objects.all():
            if dataset.short_name in globals.NOT_AS_REFERENCE:
                continue
            self.__logger.info(dataset.short_name)
            vs = dataset.versions.all()

            for version in vs:
                run = ValidationRun()
                run.start_time = datetime.now(tzlocal())
                run.save()

                ref_c = DatasetConfiguration()
                ref_c.validation = run
                ref_c.dataset = dataset
                ref_c.version = version
                ref_c.variable = dataset.variables.first()
                ref_c.save()

                run.reference_configuration = ref_c
                run.save()

                pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"),
                                             parameters="0.0, 0.2", \
                                             dataset_config=run.reference_configuration)
                pfilter.save()


                total_points, jobs = val.create_jobs(run)
                print(version)
                print(len(jobs))
                print(total_points)
                self._check_jobs(total_points, jobs)

    def test_geographic_subsetting(self):

        # austria bounding box
        min_lat = 46. # ll
        min_lon = 15.  # ll
        max_lat = 47.  # ur
        max_lon = 16.  # ur

        # we need the reader just to get the grid
        smosreader = val.create_reader(Dataset.objects.get(short_name='SMOS'),
                                       DatasetVersion.objects.get(short_name='SMOS_105_ASC'))
        gpis, lons, lats, cells = smosreader.cls.grid.get_grid_points()


        subgpis, sublons, sublats, subindex = _geographic_subsetting(gpis, lons, lats, min_lat, min_lon, max_lat,
                                                                     max_lon)

        assert len(subgpis) == 12
        assert len(sublats) == len(subgpis)
        assert len(sublons) == len(subgpis)

        assert not np.any(sublats > max_lat), "subsetting error: max_lat"
        assert not np.any(sublats < min_lat), "subsetting error: min_lat"
        assert not np.any(sublons > max_lon), "subsetting error: max_lon"
        assert not np.any(sublons < min_lon), "subsetting error: min_lon"
    
    def test_no_geographic_subsetting(self):
        # we need the reader just to get the grid
        smosreader = val.create_reader(Dataset.objects.get(short_name='SMOS'), DatasetVersion.objects.get(short_name='SMOS_105_ASC'))
        gpis, lats, lons, cells = smosreader.cls.grid.get_grid_points()


        subgpis, sublats, sublons, subindex = _geographic_subsetting(gpis, lats, lons, None, None, None, None)

        assert np.array_equal(gpis, subgpis)
        assert np.array_equal(lats, sublats)
        assert np.array_equal(lons, sublons)

    def test_geographic_subsetting_across_dateline(self):
        test_coords = [(-34.30, -221.13, 80.17, -111.44),  # dateline left
                       (-58.81, 127.61, 77.15, 256.99)  # dateline right
                       ]

        russia_gpi = 777277  # qdeg: 898557
        russia_gpi2 = 777287  # qdeg: 898567

        for min_lat, min_lon, max_lat, max_lon in test_coords:
            smos_reader = val.create_reader(Dataset.objects.get(short_name='SMOS'), DatasetVersion.objects.get(short_name='SMOS_105_ASC'))
            gpis, lats, lons, cells = smos_reader.cls.grid.get_grid_points()


            subgpis, sublats, sublons, subindex = _geographic_subsetting(gpis, lats, lons, min_lat, min_lon, max_lat,
                                                                         max_lon)

            assert len(subgpis) > 100
            assert len(sublats) == len(subgpis)
            assert len(sublons) == len(subgpis)
            assert russia_gpi in subgpis
            assert russia_gpi2 in subgpis

    def test_geographic_subsetting_shifted(self):
        ## leaflet allows users to shift the map arbitrarily to the left or right. Check that we can compensate for that
        smosreader = val.create_reader(Dataset.objects.get(short_name='SMOS'), DatasetVersion.objects.get(short_name='SMOS_105_ASC'))
        gpis, lats, lons, cells = smosreader.cls.grid.get_grid_points()


        test_coords = [(-46.55, -1214.64, 71.96, -1105.66, 1),  # americas
                       (9.79, -710.50, 70.14, -545.27, 2),  # asia
                       (-55.37, 1303.24, 68.39, 1415.03, 1),  # americas
                       (7.01, 1473.39, 68.39, 1609.80, 2),  # asia
                       ]

        panama_gpi = 463973
        india_gpi = 600607

        for min_lat, min_lon, max_lat, max_lon, area in test_coords:
            subgpis, sublats, sublons, subindex = _geographic_subsetting(gpis, lats, lons, min_lat, min_lon, max_lat,
                                                                         max_lon)

            assert len(subgpis) > 100
            assert len(sublats) == len(subgpis)
            assert len(sublons) == len(subgpis)
            if area == 1:
                assert panama_gpi in subgpis
            elif area == 2:
                assert india_gpi in subgpis

    def test_mkdir_exception(self):
        with pytest.raises(PermissionError):
            val.mkdir_if_not_exists('/root/valentina_unit_test')

    def test_first_file_in_nothing_found(self):
        result = val.first_file_in('/tmp', 'there_really_should_be_no_extension_like_this')
        assert result is None

    def test_count_gpis_exception(self):
        num = val.num_gpis_from_job(None)
        assert num == 1

    @pytest.mark.long_running
    @pytest.mark.graphs
    def test_generate_graphs(self):
        infile1 = 'testdata/output_data/cglss1_ismn.nc'
        # todo: add a second file like in the original test when there are more datasets

        # create validation object and data folder for it
        v = generate_default_validation()
        # scatterplot
        v.reference_configuration.dataset = Dataset.objects.get(short_name='ISMN')
        v.reference_configuration.save()
        run_dir = path.join(OUTPUT_FOLDER, str(v.id))
        val.mkdir_if_not_exists(run_dir)

        # copy our netcdf data file there and link it in the validation object
        # then generate the graphs

        shutil.copy(infile1, path.join(run_dir, 'results.nc'))
        val.set_outfile(v, run_dir)
        v.save()
        val.generate_all_graphs(v, run_dir)

        boxplot_pngs = [x for x in os.listdir(run_dir) if fnmatch.fnmatch(x, 'boxplot*.png')]
        self.__logger.debug(boxplot_pngs)
        n_metrics = len(globals.METRICS.keys())
        assert len(boxplot_pngs) == n_metrics

        overview_pngs = [x for x in os.listdir(run_dir) if fnmatch.fnmatch(x, 'overview*.png')]
        self.__logger.debug(overview_pngs)
        assert len(overview_pngs) == n_metrics * (v.dataset_configurations.count() - 1)

        # remove results from first test and recreate dir
        #shutil.rmtree(run_dir)
        #val.mkdir_if_not_exists(run_dir)

        self.delete_run(v)

    @pytest.mark.long_running
    def test_existing_validations(self):
        # common default settings:
        user = self.testuser
        time_intervals_from = datetime(1978, 1, 1, tzinfo=UTC)
        time_intervals_to = datetime(2018, 12, 31, tzinfo=UTC)
        anomalies_methods = ValidationRun.ANOMALIES_METHODS
        scaling_methods = [ValidationRun.MIN_MAX, ValidationRun.NO_SCALING, ValidationRun.MEAN_STD]
        run_ids = []
        # preparing a few validations, so that there is a base to be searched
        for i in range(3):
            run = generate_default_validation()
            run.user = self.testuser
            run.interval_from = time_intervals_from
            run.interval_to = time_intervals_to
            run.min_lat = self.austria_coordinates[0]
            run.min_lon = self.austria_coordinates[1]
            run.max_lat = self.austria_coordinates[2]
            run.max_lon = self.austria_coordinates[3]

            run.anomalies = anomalies_methods[i][0]
            if anomalies_methods[i][0] == 'climatology':
                run.anomalies_from = time_intervals_from
                run.anomalies_to = time_intervals_to
            run.scaling_method = scaling_methods[i]
            run.doi = f'doi-1-2-{i}'
            run.save()
            run_ids.append(run.id)

        # ================== tcols ====================================
        run_tcol = generate_default_validation_triple_coll()
        run_tcol.user = self.testuser
        run_tcol.interval_from = time_intervals_from
        run_tcol.interval_to = time_intervals_to
        run_tcol.min_lat = self.austria_coordinates[0]
        run_tcol.min_lon = self.austria_coordinates[1]
        run_tcol.max_lat = self.austria_coordinates[2]
        run_tcol.max_lon = self.austria_coordinates[3]

        run_tcol.anomalies = anomalies_methods[0][0]
        run_tcol.scaling_method = scaling_methods[0]
        run_tcol.doi = f'tcol_doi-1-2-3'
        run_tcol.save()
        run_tcol_id = run_tcol.id

        # ========= validations with filters

        run_filt = generate_default_validation()
        run_filt.user = self.testuser
        run_filt.interval_from = time_intervals_from
        run_filt.interval_to = time_intervals_to
        run_filt.min_lat = self.austria_coordinates[0]
        run_filt.min_lon = self.austria_coordinates[1]
        run_filt.max_lat = self.austria_coordinates[2]
        run_filt.max_lon = self.austria_coordinates[3]

        run_filt.anomalies = anomalies_methods[0][0]
        run_filt.scaling_method = scaling_methods[0]
        run_filt.doi = f'doi-1-2-8'
        run_filt.save()
        run_filt_id = run_filt.id

        for config in run_filt.dataset_configurations.all():
            config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            if config.dataset.short_name == globals.ISMN:
                config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
            print('old one', config.dataset == globals.ISMN, config, config.filters.all())

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='WEGENERNET', \
                                     dataset_config=run_filt.reference_configuration)
        pfilter.save()
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0,0.2", \
                                     dataset_config=run_filt.reference_configuration)
        pfilter.save()

        published_runs = ValidationRun.objects.exclude(doi='').order_by('-start_time')

        # here will be validations for asserting, I start with exactly the same validations and check if it finds them:
        for i in range(3):
            run = generate_default_validation()
            run.user = self.testuser
            run.interval_from = time_intervals_from
            run.interval_to = time_intervals_to
            run.min_lat = self.austria_coordinates[0]
            run.min_lon = self.austria_coordinates[1]
            run.max_lat = self.austria_coordinates[2]
            run.max_lon = self.austria_coordinates[3]

            run.anomalies = anomalies_methods[i][0]
            if anomalies_methods[i][0] == 'climatology':
                run.anomalies_from = time_intervals_from
                run.anomalies_to = time_intervals_to
            run.scaling_method = scaling_methods[i]
            run.save()
            is_there_one = _compare_validation_runs(run, published_runs, user)

            assert is_there_one['is_there_validation']
            assert is_there_one['val_id'] == run_ids[i]
            run.delete()

        # runs to fail:
        run = generate_default_validation()
        run.user = self.testuser
        run.interval_from = time_intervals_from
        run.interval_to = time_intervals_to

        # here different coordinates
        run.min_lat = 34
        run.min_lon = -11
        run.max_lat = 48
        run.max_lon = 71

        run.anomalies = anomalies_methods[0][0]
        run.scaling_method = scaling_methods[0]
        run.save()

        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # getting back to good coordinates
        run.min_lat = self.austria_coordinates[0]
        run.min_lon = self.austria_coordinates[1]
        run.max_lat = self.austria_coordinates[2]
        run.max_lon = self.austria_coordinates[3]

        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']
        assert is_there_one['val_id'] == run_ids[0]

        # spoiling time span:
        run.interval_from = datetime(1990, 1, 1, tzinfo=UTC)
        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        run.interval_from = time_intervals_from
        run.interval_to = datetime(2000, 1, 1, tzinfo=UTC)
        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # time span restored
        run.interval_to = time_intervals_to
        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']
        assert is_there_one['val_id'] == run_ids[0]

        # spoiling anomalies and scaling (there is no validation with anomalies set to 35 days average and min_max
        # scaling method at the same time):
        run.anomalies = anomalies_methods[1][0]
        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        run.anomalies = anomalies_methods[0][0]
        # there is no run with scaling method LINREG
        run.scaling_method = ValidationRun.LINREG
        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # restoring existing validation
        run.anomalies = anomalies_methods[2][0]
        run.scaling_method = scaling_methods[2]
        run.anomalies_from = time_intervals_from
        run.anomalies_to = time_intervals_to
        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']
        assert is_there_one['val_id'] == run_ids[2]

        # messing up with anomalies time interval:
        run.anomalies_from = datetime(1990, 1, 1, tzinfo=UTC)
        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        run.anomalies_from = time_intervals_from
        run.anomalies_to = datetime(1990, 1, 1, tzinfo=UTC)
        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # getting back to appropriate settings
        run.anomalies_to = time_intervals_to
        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # getting back to settings of the run with filters set adding filters for the run
        run.anomalies = anomalies_methods[0][0]
        run.scaling_method = scaling_methods[0]
        run.anomalies_from = None
        run.anomalies_to = None
        run.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # adding filters
        for new_config in run.dataset_configurations.all():
            new_config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            if new_config.dataset.short_name == globals.ISMN:
                new_config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))

            new_config.save()

        new_pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'),
                                         parameters='WEGENERNET', \
                                         dataset_config=run.reference_configuration)
        new_pfilter.save()
        # add filterring according to depth_range with the default values:
        new_pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"),
                                         parameters="0.0,0.2", \
                                         dataset_config=run.reference_configuration)
        new_pfilter.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)

        assert is_there_one['is_there_validation']
        assert is_there_one['val_id'] == run_filt_id

        # messing up with filters:

        cglsfilter = DataFilter.objects.get(name='FIL_ALL_VALID_RANGE')
        for new_config in run.dataset_configurations.all():
            if new_config.dataset.short_name == globals.CGLS_CSAR_SSM1km:
                new_config.filters.remove(cglsfilter)
                new_config.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)

        assert not is_there_one['is_there_validation']

        # getting back to the right settings
        for new_config in run.dataset_configurations.all():
            if new_config.dataset.short_name == globals.CGLS_CSAR_SSM1km:
                new_config.filters.add(cglsfilter)
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # removing ismn filter:
        ismn_filter = DataFilter.objects.get(name='FIL_ISMN_GOOD')
        for new_config in run.dataset_configurations.all():
            if new_config.dataset.short_name == globals.ISMN:
                new_config.filters.remove(ismn_filter)

        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # restoring the filter:
        for new_config in run.dataset_configurations.all():
            if new_config.dataset.short_name == globals.ISMN:
                new_config.filters.add(ismn_filter)
            new_config.save()
        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # messing up with parameterised filters:
        # ... with networks
        for pf in ParametrisedFilter.objects.filter(dataset_config=run.reference_configuration):
            if DataFilter.objects.get(pk=pf.filter_id).name == 'FIL_ISMN_NETWORKS':
                pf.parameters = 'WEGENERNET,COSMOS'
                pf.save()

        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        for pf in ParametrisedFilter.objects.filter(dataset_config=run.reference_configuration):
            if DataFilter.objects.get(pk=pf.filter_id).name == 'FIL_ISMN_NETWORKS':
                pf.parameters = 'COSMOS'
                pf.save()

        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # restoring networks
        for pf in ParametrisedFilter.objects.filter(dataset_config=run.reference_configuration):
            if DataFilter.objects.get(pk=pf.filter_id).name == 'FIL_ISMN_NETWORKS':
                pf.parameters = 'WEGENERNET'
                pf.save()

        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # with depths
        for pf in ParametrisedFilter.objects.filter(dataset_config=run.reference_configuration):
            if DataFilter.objects.get(pk=pf.filter_id).name == 'FIL_ISMN_DEPTH':
                pf.parameters = '0.10,0.20'
                pf.save()

        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # restoring depths
        for pf in ParametrisedFilter.objects.filter(dataset_config=run.reference_configuration):
            if DataFilter.objects.get(pk=pf.filter_id).name == 'FIL_ISMN_DEPTH':
                pf.parameters = '0.0,0.2'
                pf.save()

        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # adding a new dataset:
        data_c = DatasetConfiguration()
        data_c.validation = run
        data_c.dataset = Dataset.objects.get(short_name='CGLS_CSAR_SSM1km')
        data_c.version = DatasetVersion.objects.get(short_name='CGLS_CSAR_SSM1km_V1_1')
        data_c.variable = DataVariable.objects.get(short_name='S1_SSM')
        data_c.save()

        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        data_c.delete()

        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # checking scaling reference:
        new_ref = run.dataset_configurations.all()[0]
        run.scaling_ref = new_ref
        run.save()

        is_there_one = _compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # ================== tcols ====================================
        run_tcol = generate_default_validation_triple_coll()
        run_tcol.user = self.testuser
        run_tcol.interval_from = time_intervals_from
        run_tcol.interval_to = time_intervals_to
        run_tcol.min_lat = self.austria_coordinates[0]
        run_tcol.min_lon = self.austria_coordinates[1]
        run_tcol.max_lat = self.austria_coordinates[2]
        run_tcol.max_lon = self.austria_coordinates[3]

        run_tcol.anomalies = anomalies_methods[0][0]
        run_tcol.scaling_method = scaling_methods[0]
        run_tcol.save()
        is_there_one = _compare_validation_runs(run_tcol, published_runs, user)

        assert is_there_one['is_there_validation']
        assert is_there_one['val_id'] == run_tcol_id

        # setting tcols to False
        run_tcol.tcol = False
        run_tcol.save()

        is_there_one = _compare_validation_runs(run_tcol, published_runs, user)
        assert not is_there_one['is_there_validation']

        ValidationRun.objects.all().delete()
        DatasetConfiguration.objects.all().delete()
        ParametrisedFilter.objects.all().delete()

    def test_copy_validation(self):
        # create a validation to copy:
        run = generate_default_validation()
        run.user = self.testuser

        run.scaling_method = ValidationRun.MEAN_STD
        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)
        run.save()

        for config in run.dataset_configurations.all():
            if config == run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
            else:
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            config.save()

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='WEGENERNET', \
                                     dataset_config=run.reference_configuration)
        pfilter.save()
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0,0.2", \
                                     dataset_config=run.reference_configuration)
        pfilter.save()
        run_id = run.id
        val.run_validation(run_id)
        new_run = get_object_or_404(ValidationRun, pk=run_id)
        copied_run_info = _copy_validationrun(new_run, self.testuser)
        assert copied_run_info['run_id'] == run_id

        validations = ValidationRun.objects.exclude(pk=copied_run_info['run_id'])
        copied_run = ValidationRun.objects.get(pk=copied_run_info['run_id'])
        comparison = _compare_validation_runs(copied_run, validations, copied_run.user)

        # the query validations will be empty so 'is_there_validation' == False, 'val_id' == None, '
        # 'belongs_to_user'==False, 'is_published' == False
        assert not comparison['is_there_validation']
        assert comparison['val_id'] is None
        assert not comparison['belongs_to_user']
        assert not comparison['is_published']

        copied_run_info = _copy_validationrun(new_run, self.testuser2)
        assert copied_run_info['run_id'] != run.id

        validations = ValidationRun.objects.exclude(pk=copied_run_info['run_id'])
        copied_run = ValidationRun.objects.get(pk=copied_run_info['run_id'])
        comparison = _compare_validation_runs(copied_run, validations, copied_run.user)

        assert comparison['is_there_validation']
        assert comparison['val_id'] == run.id
        assert not comparison['belongs_to_user']
        assert not comparison['is_published']

        assert copied_run.total_points == 4
        assert copied_run.error_points == 0
        assert copied_run.ok_points == 4
        self.check_results(copied_run)

        # copying again, so to check CopiedValidations model
        new_run = get_object_or_404(ValidationRun, pk=run_id)
        _copy_validationrun(new_run, self.testuser2)

        # checking if saving to CopiedValidations model is correct (should be 2, because the first validation was
        # returned the same, and only the second and the third one were copied:
        copied_runs = CopiedValidations.objects.all()
        assert len(copied_runs) == 2
        assert copied_runs[0].used_by_user == self.testuser2

        # removing the original run should not cause removal of the record
        original_run = copied_runs[0].original_run
        self.delete_run(original_run)

        copied_runs = CopiedValidations.objects.all()
        assert len(copied_runs) == 2
        assert copied_runs[0].original_run is None

        # now I remove one of the validations
        self.delete_run(copied_run)
        # now should be 1, because copied validaitons has been removed
        copied_runs = CopiedValidations.objects.all()
        assert len(copied_runs) == 1

        # and now I'm removing the user who copied validations
        user_to_remove = self.testuser2
        user_to_remove.delete()
        copied_runs = CopiedValidations.objects.all()
        assert len(copied_runs) == 0


