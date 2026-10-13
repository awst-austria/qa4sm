import os
import shutil
import tempfile
from datetime import datetime
from types import SimpleNamespace
from unittest import mock

import netCDF4
import numpy as np
import pandas as pd
import pytest
from dateutil.tz import tzlocal
from django.test import TestCase

import validator.validation as val
from validator.models import DataFilter
from validator.models import Dataset
from validator.models import DatasetConfiguration
from validator.models import DatasetVersion
from validator.models import ParametrisedFilter
from validator.models import ValidationRun
from validator.tests.testutils import set_dataset_paths
from validator.validation.adapters import MergeSensorsAdapter
from validator.validation.validation import register_station_selection


class StubIsmn:
    """Reader that returns a fixed frame per sensor id and logs the reads."""

    def __init__(self, frames):
        self.frames = frames
        self.reads = []

    def read(self, gpi, *args, **kwargs):
        self.reads.append(int(gpi))
        return self.frames[int(gpi)]


def stub_validation(reader):
    return SimpleNamespace(data_manager=SimpleNamespace(
        reference_name='ISMN', datasets={'ISMN': {'class': reader}}))


def frame(values, start='2020-01-01'):
    index = pd.date_range(start, periods=len(values), freq='D')
    return pd.DataFrame({'sm': values}, index=index)


def job(gpis, metas):
    gpis = np.array(gpis)
    zeros = np.zeros(len(gpis))
    return gpis, zeros, zeros, np.array(metas)


class TestRegisterStationSelection:

    def test_merged_and_failed_stations_are_registered(self):
        stub = StubIsmn({})
        adapter = MergeSensorsAdapter(stub, variable='sm')
        register_station_selection(stub_validation(adapter), job(
            [0, 3, 4],
            [{'other_ids': [1, 2]},
             {'other_ids': [], 'selection_failed': True},
             {'other_ids': []}]))

        assert stub._merge_sensors == {0: [1, 2]}
        assert stub._selection_failed == {3}

    def test_jobs_without_metadata_are_ignored(self):
        stub = StubIsmn({})
        adapter = MergeSensorsAdapter(stub, variable='sm')
        register_station_selection(stub_validation(adapter),
                                   job([0], [{}])[:3])

        assert not hasattr(stub, '_merge_sensors')
        assert not hasattr(stub, '_selection_failed')


class TestMergeSensorsAdapter:

    def test_failed_station_is_read_empty_without_reading(self):
        stub = StubIsmn({3: frame([0.1, 0.2])})
        adapter = MergeSensorsAdapter(stub, variable='sm')
        register_station_selection(stub_validation(adapter), job(
            [3], [{'other_ids': [], 'selection_failed': True}]))

        data = adapter.read(3)

        assert data.empty
        assert list(data.columns) == ['sm']
        assert isinstance(data.index, pd.DatetimeIndex)
        assert stub.reads == []

    def test_merged_station_is_averaged_on_common_timestamps(self):
        stub = StubIsmn({0: frame([0.1, 0.2, 0.3]),
                         1: frame([0.3, 0.4, 0.5], start='2020-01-02')})
        adapter = MergeSensorsAdapter(stub, variable='sm')
        register_station_selection(stub_validation(adapter), job(
            [0], [{'other_ids': [1]}]))

        data = adapter.read(0)

        assert list(data.index) == list(
            pd.date_range('2020-01-02', periods=2, freq='D'))
        np.testing.assert_allclose(data['sm'].values, [0.25, 0.35])

    def test_unregistered_station_is_read_as_is(self):
        stub = StubIsmn({0: frame([0.1, 0.2])})
        adapter = MergeSensorsAdapter(stub, variable='sm')

        data = adapter.read(0)

        np.testing.assert_allclose(data['sm'].values, [0.1, 0.2])


class TestCreateJobsSensorMerging(TestCase):
    """
    ISMN_V20180712_MINI: SCAN/Kainaliu has two sensors at 0.0508 m, all
    other stations have a single sensor.
    """
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

    def setUp(self):
        set_dataset_paths()

        self.run = ValidationRun()
        self.run.start_time = datetime.now(tzlocal())
        self.run.save()

        version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
        config = DatasetConfiguration()
        config.validation = self.run
        config.dataset = Dataset.objects.get(short_name='ISMN')
        config.version = version
        config.variable = version.variables.first()
        config.save()
        self.run.spatial_reference_configuration = config
        self.run.save()

        ParametrisedFilter(
            filter=DataFilter.objects.get(name='FIL_ISMN_DEPTH'),
            parameters='0.0,0.1', dataset_config=config).save()

    def create_jobs(self, tolerances):
        config = self.run.spatial_reference_configuration
        ParametrisedFilter(
            filter=DataFilter.objects.get(name='FIL_ISMN_TOLERANCES'),
            parameters=tolerances, dataset_config=config).save()
        reader, _, _ = val.validation._get_spatial_reference_reader(self.run)
        total_points, jobs = val.create_jobs(self.run, reader, config)

        # candidate stations: sensors in the tolerance-widened 0 - 0.1 m layer
        top_tol, bottom_tol = (float(t) for t in tolerances.split(','))
        stations = reader.get_dataset_ids(
            'soil_moisture', 0.0 - top_tol, 0.1 + bottom_tol,
            groupby=['network', 'station'])
        kainaliu = [j for j in jobs if j[3][0]['station'] == 'Kainaliu']
        return total_points, jobs, stations, kainaliu

    def test_failed_station_is_kept_as_placeholder(self):
        total_points, jobs, stations, kainaliu = self.create_jobs('0.0,0.0')

        # every station is a job, also those that failed the selection
        assert total_points == len(jobs) == len(stations)
        assert len(kainaliu) == 1
        meta = kainaliu[0][3][0]
        assert meta['selection_failed'] is True
        assert meta['selection_reason'] == 'depth'
        assert meta['instrument'] == 'Tolerance selection failed'
        assert meta['frm_class'] == 'None'
        assert meta['other_ids'] == []

    def test_station_within_tolerance_is_merged(self):
        total_points, jobs, stations, kainaliu = self.create_jobs('0.1,0.1')

        assert total_points == len(jobs) == len(stations)
        meta = kainaliu[0][3][0]
        assert 'selection_failed' not in meta
        assert meta['instrument'] == '2 Averaged Sensors'
        assert len(meta['other_ids']) == 1

    def test_spatial_validation_is_rejected(self):
        self.run.val_type = ValidationRun.VAL_TYPE_SPATIAL
        self.run.save()

        with pytest.raises(ValueError, match='temporal'):
            self.create_jobs('0.1,0.1')


class TestSaveValidationConfigSensorMerging(TestCase):
    """The results file flags merged ISMN sensors for qa4sm-reader."""
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

    def setUp(self):
        self.out_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.out_dir)
        self.nc_name = 'results.nc'
        with netCDF4.Dataset(os.path.join(self.out_dir, self.nc_name), 'w'):
            pass

        self.run = ValidationRun()
        self.run.start_time = datetime.now(tzlocal())
        self.run.output_file.name = self.nc_name
        self.run.save()

        version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
        self.config = DatasetConfiguration()
        self.config.validation = self.run
        self.config.dataset = Dataset.objects.get(short_name='ISMN')
        self.config.version = version
        self.config.variable = version.variables.first()
        self.config.save()
        self.run.spatial_reference_configuration = self.config
        self.run.save()

    def saved_attrs(self):
        with mock.patch('validator.validation.validation.OUTPUT_FOLDER',
                        self.out_dir):
            val.validation.save_validation_config(self.run)
        with netCDF4.Dataset(os.path.join(self.out_dir, self.nc_name)) as ds:
            return {key: ds.getncattr(key) for key in ds.ncattrs()}

    def test_merging_is_flagged(self):
        ParametrisedFilter(
            filter=DataFilter.objects.get(name='FIL_ISMN_TOLERANCES'),
            parameters='0.1,0.1', dataset_config=self.config).save()

        attrs = self.saved_attrs()

        assert attrs['val_dc_ismn_sensor_merging0'] == 'True'

    def test_no_flag_without_merging(self):
        ParametrisedFilter(
            filter=DataFilter.objects.get(name='FIL_ISMN_DEPTH'),
            parameters='0.0,0.1', dataset_config=self.config).save()

        attrs = self.saved_attrs()

        # the configuration itself was written
        assert attrs['val_dc_dataset0'] == 'ISMN'
        assert 'val_dc_ismn_sensor_merging0' not in attrs
