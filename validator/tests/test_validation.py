from datetime import datetime
import os, errno
import time
from zipfile import ZipFile

from dateutil.tz import tzlocal
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from validator.validation.graphics import generate_all_graphs
from os import path
import shutil
from django.test import TestCase
import netCDF4
import pytest
from pytz import UTC

import numpy as np
import pandas as pd
from validator.models import DataFilter
from validator.models import DataVariable
from validator.models import Dataset
from validator.models import DatasetVersion
from validator.models import ValidationRun
import validator.validation as val
from validator.validation.globals import OUTPUT_FOLDER


class TestValidation(TestCase):

    def setUp(self):
        self.always_eager = None
        if hasattr(settings, 'CELERY_TASK_ALWAYS_EAGER'):
            self.always_eager = settings.CELERY_TASK_ALWAYS_EAGER

        settings.CELERY_TASK_ALWAYS_EAGER = True # run without parallelisation, everything in one process

        self.metrics = ['gpi', 'lon', 'lat'] + list(val.METRICS.keys())

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

    def tearDown(self):
        settings.CELERY_TASK_ALWAYS_EAGER = self.always_eager

    def generate_default_validation(self):
        run = ValidationRun()
        run.start_time = datetime.now(tzlocal())
        run.data_dataset = Dataset.objects.get(short_name='C3S')
        run.data_version = DatasetVersion.objects.get(short_name='C3S_V201706')
        run.data_variable = DataVariable.objects.get(short_name='C3S_sm')

        run.ref_dataset = Dataset.objects.get(short_name='ISMN')
        run.ref_version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
        run.ref_variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')

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
        with netCDF4.Dataset(run.output_file.path) as ds:
            for variable in self.metrics:
                values = ds.variables[variable][:]
                assert values is not None

                if length == -1:
                    length = len(values)
                    assert length > 0, 'Variable {} has no entries'.format(variable)
                else:
                    assert len(values) == length, 'Variable {} doesn\'t match other variables in length'.format(variable)

                nan_ratio = np.sum(np.isnan(values.data)) / float(len(values))
                assert nan_ratio <= 0.35, 'Variable {} has too many NaNs. Ratio: {}'.format(variable, nan_ratio)

            if(run.interval_from is None):
                assert ds.val_interval_from == "N/A", 'Wrong validation config attribute. [interval_from]'
            else:
                assert ds.val_interval_from == run.interval_from.strftime('%Y-%m-%d %H:%M'),'Wrong validation config attribute. [interval_from]'

            if(run.interval_to is None):
                assert ds.val_interval_to == "N/A", 'Wrong validation config attribute. [interval_to]'
            else:
                assert ds.val_interval_to == run.interval_to.strftime('%Y-%m-%d %H:%M'),'Wrong validation config attribute. [interval_to]'

            if not run.data_filters.all():
                assert ds.val_data_filters == 'N/A'
            else:
                assert ds.val_data_filters, 'Validation config attribute empty. [data_filters]'
                assert (ds.val_data_filters.count(';') + 1) == len(run.data_filters.all()), 'Validation config attribute has wrong number of elements. [data_filters]'

            if not run.ref_filters.all():
                assert ds.val_ref_filters == 'N/A'
            else:
                assert ds.val_ref_filters, 'Validation config attribute empty. [ref_filters]'
                assert (ds.val_ref_filters.count(';') + 1) == len(run.ref_filters.all()), 'Validation config attribute has wrong number of elements. [ref_filters]'

            assert ds.val_data_dataset == run.data_dataset.pretty_name,' Wrong validation config attribute. [data_dataset]'
            assert ds.val_data_version == run.data_version.pretty_name,' Wrong validation config attribute. [data_version]'
            assert ds.val_data_variable == run.data_variable.pretty_name,' Wrong validation config attribute. [data_variable]'
            assert ds.val_ref_dataset == run.ref_dataset.pretty_name,' Wrong validation config attribute. [ref_dataset]'
            assert ds.val_ref_version == run.ref_version.pretty_name,' Wrong validation config attribute. [ref_version]'
            assert ds.val_ref_variable == run.ref_variable.pretty_name,' Wrong validation config attribute. [ref_variable]'

            assert ds.val_scaling_ref == run.scaling_ref,' Wrong validation config attribute. [scaling_ref]'
            assert ds.val_scaling_method == run.scaling_method,' Wrong validation config attribute. [scaling_method]'

        # check zipfile of graphics
        zipfile = os.path.join(outdir, 'graphs.zip')
        assert os.path.isfile(zipfile)
        with ZipFile(zipfile, 'r') as myzip:
            assert myzip.testzip() is None

        # check graphics
        for metric in val.METRICS:
            filename = 'boxplot_{}.png'.format(metric)
            filename = os.path.join(outdir, filename)
            assert os.path.isfile(filename)
            filename2 = 'overview_{}.png'.format(metric)
            filename2 = os.path.join(outdir, filename2)
            assert os.path.isfile(filename2)

    ## delete output of test validations, clean up after ourselves
    def delete_run(self, run):
        # let's see if the output file gets cleaned up when the model is deleted
        ncfile = run.output_file.path
        outdir = os.path.dirname(ncfile)
        assert os.path.isfile(ncfile)
        run.delete()
        assert not os.path.exists(outdir)

    @pytest.mark.filterwarnings("ignore:No results for gpi:UserWarning") # ignore pytesmo warnings about missing results
    def test_validation(self):
        run = self.generate_default_validation()
        run.user = self.testuser

        run.scaling_ref = ValidationRun.SCALE_REF
        run.scaling_method = ValidationRun.CDF_MATCH # cdf matching causes an error for 1 gpi, use that to test error handling

        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)

        run.save() ## need to save before adding filters because django m2m relations work that way

        run.data_filters.add(DataFilter.objects.get(name='FIL_C3S_FLAG_0'))
        run.data_filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        run.ref_filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))

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

        run.ref_dataset = Dataset.objects.get(short_name='GLDAS')
        run.ref_version = DatasetVersion.objects.get(short_name='GLDAS_TEST')
        run.ref_variable = DataVariable.objects.get(short_name='GLDAS_SoilMoi0_10cm_inst')

        run.interval_from = datetime(2005, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2006, 1, 1, tzinfo=UTC)

        run.save() ## need to save before adding filters because django m2m relations work that way

        run.data_filters.add(DataFilter.objects.get(name='FIL_C3S_FLAG_0'))
        run.data_filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

        run.ref_filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
        run.ref_filters.add(DataFilter.objects.get(name='FIL_GLDAS_UNFROZEN'))

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

    @pytest.mark.filterwarnings("ignore:No results for gpi:UserWarning") # ignore pytesmo warnings about missing results
    @pytest.mark.long_running
    def test_validation_ascat(self):
        run = self.generate_default_validation()
        run.user = self.testuser
        run.data_dataset = Dataset.objects.get(short_name='ASCAT')
        run.data_version = DatasetVersion.objects.get(short_name='ASCAT_H113')
        run.data_variable = DataVariable.objects.get(short_name='ASCAT_sm')

        run.scaling_ref = ValidationRun.SCALE_REF
        run.scaling_method = ValidationRun.CDF_MATCH # cdf matching causes an error for 1 gpi, use that to test error handling

        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)

        run.save() ## need to save before adding filters because django m2m relations work that way

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
                            data = msk_reader.read_ts(16.366667, 48.2)
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
                run.ref_dataset = dataset
                run.ref_version = version
                run.ref_variable = dataset.variables.first()

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

#     @pytest.mark.long_running
    def test_generate_graphs(self):
        infile1 = 'testdata/c3s_ismn.nc'
        infile2 = 'testdata/c3s_gldas.nc'

        # create validation object and data folder for it
        v = self.generate_default_validation()
        v.ref_dataset = Dataset.objects.get(short_name='ISMN')
        v.save()
        run_dir = path.join(OUTPUT_FOLDER, str(v.id))
        val.mkdir_if_not_exists(run_dir)

        # copy our netcdf data file there and link it in the validation object
        # then generate the graphs

        # heatmap
        shutil.copy(infile1, path.join(run_dir, 'results.nc'))
        val.set_outfile(v, run_dir)
        v.save()
        val.generate_all_graphs(v, run_dir)

        # we should have at least 12 files in that directory
        assert len(os.listdir(run_dir)) >= 12

        # remove results from first test and recreate dir
        shutil.rmtree(run_dir)
        val.mkdir_if_not_exists(run_dir)

        # do the same for the other netcdf file
        # scatterplot
        shutil.copy(infile2, path.join(run_dir, 'results.nc'))
        val.set_outfile(v, run_dir)
        v.ref_dataset = Dataset.objects.get(short_name='GLDAS')
        v.save()
        val.generate_all_graphs(v, run_dir)

        assert len(os.listdir(run_dir)) >= 12

        self.delete_run(v)
