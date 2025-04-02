'''
Because even (or especially?) hacks should be tested
'''

from pathlib import Path
import os

from c3s_sm.interface import C3STs as c3s_read
from django.test import TestCase
from ismn.interface import ISMN_Interface
from ismn.custom import CustomSensorMetadataCsv

import numpy as np
from validator.hacks import TimezoneAdapter
from validator.models import Dataset
from validator.tests.testutils import set_dataset_paths

import shutil


def cleanup_metadata(ISMN_storage_path):
    # clean existing metadata; needed in case changes are made to the ismn
    # reader
    paths_to_metadata = ISMN_storage_path.glob('**/python_metadata')
    for path in paths_to_metadata:
        shutil.rmtree(path)


class TestHacks(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

    def setUp(self):
        set_dataset_paths()

    @staticmethod
    def gen_ismn_interface(ismn_data_folder):
        if os.path.isfile(
                os.path.join(ismn_data_folder, 'frm_classification.csv')):
            custom_meta_readers = [
                CustomSensorMetadataCsv(
                    os.path.join(ismn_data_folder, 'frm_classification.csv'),
                    fill_values={'frm_class': 'undeducible'},
                ),
            ]
        else:
            custom_meta_readers = None

        reader = ISMN_Interface(ismn_data_folder,
                                custom_meta_reader=custom_meta_readers)

        return reader


    def test_timezone_adapter(self):
        c3s_storage_path = Path(
            Dataset.objects.get(short_name='C3S_combined').storage_path)
        c3s_data_folder = c3s_storage_path.joinpath(
            'C3S_V201706/TCDR/063_images_to_ts/combined-daily')
        c3s_reader = c3s_read(c3s_data_folder)

        timezone_reader = TimezoneAdapter(c3s_reader)

        orig_data = c3s_reader.read(-155.42, 19.78)
        data = timezone_reader.read(-155.42, 19.78)
        self.assertTrue(
            np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue(not hasattr(data.index, 'tz') or data.index.tz is None)

        orig_data = c3s_reader.read(-155.42, 19.78)
        data = timezone_reader.read(-155.42, 19.78)
        self.assertTrue(
            np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue(
            (not hasattr(data.index, 'tz')) or (data.index.tz is None))

        ismn_storage_path = Path(
            Dataset.objects.get(short_name='ISMN').storage_path)
        cleanup_metadata(ismn_storage_path)

        ismn_data_folder = ismn_storage_path.joinpath('ISMN_V20191211')
        ismn_reader = self.gen_ismn_interface(ismn_data_folder)

        timezone_reader2 = TimezoneAdapter(ismn_reader)

        orig_data = ismn_reader.read_ts(0)
        data = timezone_reader2.read_ts(0)
        self.assertTrue(
            np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue(
            (not hasattr(data.index, 'tz')) or (data.index.tz is None))
