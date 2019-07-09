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

from django.contrib.auth import get_user_model
User = get_user_model()

from dateutil.tz import tzlocal
from django.test import TestCase
from django.test.utils import override_settings
import netCDF4
import pytest
from pytz import UTC

import numpy as np
import pandas as pd
from validator.models import DataFilter
from validator.models import DataVariable
from validator.models import Dataset
from validator.models import DatasetConfiguration
from validator.models import DatasetVersion
from validator.models import ValidationRun
import validator.validation as val
from validator.validation.globals import METRICS
from validator.validation.globals import OUTPUT_FOLDER


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestValidation(TestCase):

    fixtures = ['variables', 'versions', 'datasets', 'filters']

    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.metrics = ['gpi', 'lon', 'lat'] + list(METRICS.keys())

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

    def generate_default_validation(self):
        run = ValidationRun()
        run.start_time = datetime.now(tzlocal())
        run.save()

        data_c = DatasetConfiguration()
        data_c.validation = run
        data_c.dataset = Dataset.objects.get(short_name='C3S')
        data_c.version = DatasetVersion.objects.get(short_name='C3S_V201706')
        data_c.variable = DataVariable.objects.get(short_name='C3S_sm')
        data_c.save()

        ref_c = DatasetConfiguration()
        ref_c.validation = run
        ref_c.dataset = Dataset.objects.get(short_name='ISMN')
        ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
        ref_c.variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')
        ref_c.save()

        run.reference_configuration = ref_c
        run.scaling_ref = ref_c
        run.save()

        return run

    ## check output of validation
    def check_results(self, run):
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
        with netCDF4.Dataset(run.output_file.path, mode='r') as ds:
            ## check the metrics contained in thef ile
            for metric in self.metrics:
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

            if(run.interval_from is None):
                assert ds.val_interval_from == "N/A", 'Wrong validation config attribute. [interval_from]'
            else:
                assert ds.val_interval_from == run.interval_from.strftime('%Y-%m-%d %H:%M'), 'Wrong validation config attribute. [interval_from]'

            if(run.interval_to is None):
                assert ds.val_interval_to == "N/A", 'Wrong validation config attribute. [interval_to]'
            else:
                assert ds.val_interval_to == run.interval_to.strftime('%Y-%m-%d %H:%M'), 'Wrong validation config attribute. [interval_to]'

            for d_index, dataset_config in enumerate(run.dataset_configurations.all()):
                ds_name = 'val_dc_dataset' + str(d_index)
                stored_dataset = ds.getncattr(ds_name)
                stored_version = ds.getncattr('val_dc_version' + str(d_index))
                stored_variable = ds.getncattr('val_dc_variable' + str(d_index))
                stored_filters = ds.getncattr('val_dc_filters' + str(d_index))

                # check dataset, version, variable
                assert stored_dataset == dataset_config.dataset.short_name, 'Wrong dataset config attribute. [dataset]'
                assert stored_version == dataset_config.version.short_name, 'Wrong dataset config attribute. [version]'
                assert stored_variable == dataset_config.variable.short_name, 'Wrong dataset config attribute. [variable]'

                # check filters
                if not dataset_config.filters.all():
                    assert stored_filters == 'N/A', 'Wrong dataset config filters (should be none)'
                else:
                    assert stored_filters, 'Wrong dataset config filters (shouldn\'t be empty)'
                    for fil in dataset_config.filters.all():
                        assert fil.description in stored_filters, 'Wrong dataset config filters'

                # check reference
                if dataset_config.id == run.reference_configuration.id:
                    assert ds.val_ref == ds_name, 'Wrong validation config attribute. [reference_configuration]'

                if dataset_config.id == run.scaling_ref.id:
                    assert ds.val_scaling_ref == ds_name, 'Wrong validation config attribute. [scaling_ref]'

            assert ds.val_scaling_method == run.scaling_method,' Wrong validation config attribute. [scaling_method]'

        # check zipfile of graphics
        zipfile = os.path.join(outdir, 'graphs.zip')
        assert os.path.isfile(zipfile)
        with ZipFile(zipfile, 'r') as myzip:
            assert myzip.testzip() is None

        # check diagrams
        boxplot_pngs = [ x for x in os.listdir(outdir) if fnmatch.fnmatch(x, 'boxplot*.png')]
        self.__logger.debug(boxplot_pngs)
        assert len(boxplot_pngs) == 12

        overview_pngs = [ x for x in os.listdir(outdir) if fnmatch.fnmatch(x, 'overview*.png')]
        self.__logger.debug(overview_pngs)
        assert len(overview_pngs) == 12 * (run.dataset_configurations.count() - 1)

    ## delete output of test validations, clean up after ourselves
    def delete_run(self, run):
        # let's see if the output file gets cleaned up when the model is deleted

        ncfile = run.output_file.path
        outdir = os.path.dirname(ncfile)
        assert os.path.isfile(ncfile)
        run.delete()
        assert not os.path.exists(outdir)

    @pytest.mark.filterwarnings("ignore:No results for gpi:UserWarning") # ignore pytesmo warnings about missing results
    @pytest.mark.filterwarnings("ignore:read_ts is deprecated, please use read instead:DeprecationWarning") # ignore pytesmo warnings about read_ts
    def test_validation(self):
        run = self.generate_default_validation()
        run.user = self.testuser

        #run.scaling_ref = ValidationRun.SCALE_REF
        run.scaling_method = ValidationRun.CDF_MATCH # cdf matching causes an error for 1 gpi, use that to test error handling

        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)

        run.save()

        for config in run.dataset_configurations.all():
            if config == run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
            else:
                config.filters.add(DataFilter.objects.get(name='FIL_C3S_FLAG_0'))
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

            config.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run.total_points == 4
        assert new_run.error_points == 0
        assert new_run.ok_points == 4
        self.check_results(new_run)
        self.delete_run(new_run)

    @pytest.mark.filterwarnings("ignore:No results for gpi:UserWarning")
    @pytest.mark.filterwarnings("ignore:No data for:UserWarning")
    @pytest.mark.long_running
    def test_validation_gldas_ref(self):
        run = self.generate_default_validation()
        run.user = self.testuser

        run.reference_configuration.dataset = Dataset.objects.get(short_name='GLDAS')
        run.reference_configuration.version = DatasetVersion.objects.get(short_name='GLDAS_TEST')
        run.reference_configuration.variable = DataVariable.objects.get(short_name='GLDAS_SoilMoi0_10cm_inst')
        run.reference_configuration.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        run.reference_configuration.filters.add(DataFilter.objects.get(name='FIL_GLDAS_UNFROZEN'))
        run.reference_configuration.save()

        run.interval_from = datetime(2005, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2006, 1, 1, tzinfo=UTC)

        run.save()

        for config in run.dataset_configurations.all():
            if config != run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_C3S_FLAG_0'))
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            config.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run

        assert new_run.total_points == 51
        assert new_run.error_points == 0
        assert new_run.ok_points == 51
        self.check_results(new_run)
        self.delete_run(new_run)

    @pytest.mark.long_running
    def test_validation_era_ref(self):
        run = self.generate_default_validation()
        run.user = self.testuser

        run.reference_configuration.dataset = Dataset.objects.get(short_name='ERA')
        run.reference_configuration.version = DatasetVersion.objects.get(short_name='ERA5_test')
        run.reference_configuration.variable = DataVariable.objects.get(short_name='ERA_sm')
        run.reference_configuration.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        run.reference_configuration.filters.add(DataFilter.objects.get(name='FIL_ERA_TEMP_UNFROZEN'))
        run.reference_configuration.save()

        run.interval_from = datetime(2005, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2006, 1, 1, tzinfo=UTC)

        run.save()

        for config in run.dataset_configurations.all():
            if config != run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_C3S_FLAG_0'))
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            config.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run, "Didn't find validation in database"

        assert new_run.total_points == 400, "Number of gpis is off"
        assert new_run.error_points == 0, "Too many error gpis"
        assert new_run.ok_points == 400, "OK points are off"
        self.check_results(new_run)
        self.delete_run(new_run)

    @pytest.mark.filterwarnings("ignore:No results for gpi:UserWarning") # ignore pytesmo warnings about missing results
    @pytest.mark.long_running
    def test_validation_ascat(self):
        run = self.generate_default_validation()
        run.user = self.testuser

        for config in run.dataset_configurations.all():
            if config != run.reference_configuration:
                config.dataset = Dataset.objects.get(short_name='ASCAT')
                config.version = DatasetVersion.objects.get(short_name='ASCAT_H113')
                config.variable = DataVariable.objects.get(short_name='ASCAT_sm')
                config.filters.clear()
                config.save()

        #run.scaling_ref = ValidationRun.SCALE_REF
        run.scaling_method = ValidationRun.CDF_MATCH # cdf matching causes an error for 1 gpi, use that to test error handling

        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)

        run.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run.total_points == 4
        assert new_run.error_points == 0
        assert new_run.ok_points == 4
        self.check_results(new_run)
        self.delete_run(new_run)

    # test the validation with no changes to the default validation parameters
    def test_validation_default(self):
        ## create default validation object
        run = self.generate_default_validation()
        run.user = self.testuser

        run.save()
        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        ## fetch results from db
        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run.total_points == 4
        assert new_run.error_points == 0
        assert new_run.ok_points == 4
        self.check_results(new_run)
        self.delete_run(new_run)

    @pytest.mark.long_running
    def test_validation_anomalies(self):
        run = self.generate_default_validation()
        run.user = self.testuser

        run.anomalies = True

        run.reference_configuration.dataset = Dataset.objects.get(short_name='GLDAS')
        run.reference_configuration.version = DatasetVersion.objects.get(short_name='GLDAS_TEST')
        run.reference_configuration.variable = DataVariable.objects.get(short_name='GLDAS_SoilMoi0_10cm_inst')
        run.reference_configuration.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        run.reference_configuration.filters.add(DataFilter.objects.get(name='FIL_GLDAS_UNFROZEN'))
        run.reference_configuration.save()

        run.save()

        for config in run.dataset_configurations.all():
            if config != run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_C3S_FLAG_0'))
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            config.save()

        run_id = run.id

        ## run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run
        assert new_run.total_points == 51
        assert new_run.error_points == 0
        assert new_run.ok_points == 51
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

#         no_masking_reader = val.setup_filtering(None, None, None, None)
#         assert not no_masking_reader

    def test_readers(self):
        start_time = time.time()

        datasets = Dataset.objects.all()
        for dataset in datasets:
            vs = dataset.versions.all()
            for version in vs:
                print("Testing {} version {}".format(dataset, version))

                reader = val.create_reader(dataset, version)

                assert reader is not None
                if dataset.short_name == val.globals.ISMN:
                    data = reader.read_ts(0)
                else:
                    data = reader.read_ts(16.366667, 48.2) ## vienna calling...
                assert data is not None
                assert isinstance(data, pd.DataFrame)

        print("Test duration: {}".format(time.time() - start_time))

    # minimal test of filtering, quicker than the full test below
    def test_setup_filtering_min(self):
        dataset = Dataset.objects.get(short_name='ISMN')
        version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
        variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')
        reader = val.create_reader(dataset, version)
        data_filters = [
            DataFilter.objects.get(name="FIL_ALL_VALID_RANGE"),
            DataFilter.objects.get(name="FIL_ISMN_GOOD"),
            ]
        msk_reader = val.setup_filtering(reader, data_filters, dataset, variable)

        assert msk_reader is not None
        data = msk_reader.read_ts(0)
        assert data is not None
        assert isinstance(data, pd.DataFrame)
        assert len(data.index) > 1
        assert not data[variable.pretty_name].empty
        assert not np.any(data[variable.pretty_name].values < 0)
        assert not np.any(data[variable.pretty_name].values > 100)

    # test all combinations of datasets, versions, variables, and filters
    @pytest.mark.long_running
    def test_setup_filtering_max(self):
        start_time = time.time()

        for dataset in Dataset.objects.all():
            vs = dataset.versions.all()
            va = dataset.variables.all()
            fils = dataset.filters.all()

            for version in vs:
                reader = val.create_reader(dataset, version)
                for variable in va:
                    for data_filter in fils:
                        print("Testing {} version {} variable {} filter {}".format(dataset, version, variable, data_filter.name))
                        msk_reader = val.setup_filtering(reader, [data_filter], dataset, variable)
                        assert msk_reader is not None
                        if dataset.short_name == val.globals.ISMN:
                            data = msk_reader.read_ts(0)
                        else:
                            data = msk_reader.read_ts(16.6, 48.2)
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
            print(dataset.short_name)
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

                total_points, jobs = val.create_jobs(run)
                print(version)
                print(len(jobs))
                print(total_points)
                self._check_jobs(total_points, jobs)

    def test_mkdir_exception(self):
        with pytest.raises(PermissionError):
            val.mkdir_if_not_exists('/root/valentina_unit_test')

    def test_first_file_in_nothing_found(self):
        result = val.first_file_in('/tmp', 'there_really_should_be_no_extension_like_this')
        assert result is None

    def test_count_gpis_exception(self):
        num = val.num_gpis_from_job(None)
        assert num == 1

#     @pytest.mark.long_running
    def test_generate_graphs(self):
        infile1 = 'testdata/c3s_ismn.nc'
        infile2 = 'testdata/c3s_gldas.nc'

        # create validation object and data folder for it
        v = self.generate_default_validation()
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

        boxplot_pngs = [ x for x in os.listdir(run_dir) if fnmatch.fnmatch(x, 'boxplot*.png')]
        self.__logger.debug(boxplot_pngs)
        assert len(boxplot_pngs) == 8

        overview_pngs = [ x for x in os.listdir(run_dir) if fnmatch.fnmatch(x, 'overview*.png')]
        self.__logger.debug(overview_pngs)
        assert len(overview_pngs) == 8 * (v.dataset_configurations.count() - 1)

        # remove results from first test and recreate dir
        shutil.rmtree(run_dir)
        val.mkdir_if_not_exists(run_dir)

        # do the same for the other netcdf file
        shutil.copy(infile2, path.join(run_dir, 'results.nc'))
        val.set_outfile(v, run_dir)
        # heatmap
        v.reference_configuration.dataset = Dataset.objects.get(short_name='GLDAS')
        v.reference_configuration.save()
        val.generate_all_graphs(v, run_dir)

        boxplot_pngs = [ x for x in os.listdir(run_dir) if fnmatch.fnmatch(x, 'boxplot*.png')]
        self.__logger.debug(boxplot_pngs)
        assert len(boxplot_pngs) == 8

        overview_pngs = [ x for x in os.listdir(run_dir) if fnmatch.fnmatch(x, 'overview*.png')]
        self.__logger.debug(overview_pngs)
        assert len(overview_pngs) == 8 * (v.dataset_configurations.count() - 1)

        self.delete_run(v)

    @pytest.mark.long_running
    def test_era_graph(self):
        infile1 = 'testdata/2-ERA.swvl1_with_1-C3S.sm.nc'


        # create validation object and data folder for it
        v = self.generate_default_validation()
        # scatterplot
        v.reference_configuration.dataset = Dataset.objects.get(short_name='ERA')
        v.reference_configuration.save()
        run_dir = path.join(OUTPUT_FOLDER, str(v.id))
        val.mkdir_if_not_exists(run_dir)

        # copy our netcdf data file there and link it in the validation object
        # then generate the graphs

        shutil.copy(infile1, path.join(run_dir, 'results.nc'))
        val.set_outfile(v, run_dir)
        v.save()
        val.generate_all_graphs(v, run_dir)

        boxplot_pngs = [ x for x in os.listdir(run_dir) if fnmatch.fnmatch(x, 'boxplot*.png')]
        self.__logger.debug(boxplot_pngs)
        assert len(boxplot_pngs) == 12

        overview_pngs = [ x for x in os.listdir(run_dir) if fnmatch.fnmatch(x, 'overview*.png')]
        self.__logger.debug(overview_pngs)
        assert len(overview_pngs) == 12 * (v.dataset_configurations.count() - 1)

        # remove results
        shutil.rmtree(run_dir)
