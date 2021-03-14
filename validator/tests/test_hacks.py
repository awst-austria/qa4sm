'''
Because even (or especially?) hacks should be tested
'''

from os import path

from validator.validation.input_readers.cgls_s1_readers import CglsS1TiffReader
from django.test import TestCase
from ismn.interface import ISMN_Interface

import numpy as np
from validator.hacks import TimezoneAdapter
from validator.models import Dataset
from validator.tests.testutils import set_dataset_paths


class TestHacks(TestCase):

    fixtures = ['variables', 'versions', 'datasets', 'filters']

    def setUp(self):
        set_dataset_paths()

    def test_timezone_adapter(self):
        cgls_data_folder = path.join(Dataset.objects.get(short_name='CGLS_CSAR_SSM1km').storage_path, 'CGLS_CSAR_SSM1km_V1_1/tiff')
        cgls_reader = CglsS1TiffReader(cgls_data_folder, param='CGLS_SSM')

        timezone_reader = TimezoneAdapter(cgls_reader)

        orig_data = cgls_reader.read_ts(15.8, 47.9) 
        data = timezone_reader.read_ts(15.8, 47.9)
        self.assertTrue(np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue(not hasattr(data.index, 'tz') or data.index.tz is None)

        orig_data = cgls_reader.read(15.8, 47.9)
        data = timezone_reader.read(15.8, 47.9)
        self.assertTrue(np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue((not hasattr(data.index, 'tz')) or (data.index.tz is None))

        ismn_data_folder = path.join(Dataset.objects.get(short_name='ISMN').storage_path, 'ISMN_V20191211')
        ismn_reader = ISMN_Interface(ismn_data_folder)

        timezone_reader2 = TimezoneAdapter(ismn_reader)

        orig_data = ismn_reader.read_ts(0)
        data = timezone_reader2.read_ts(0)
        self.assertTrue(np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue((not hasattr(data.index, 'tz')) or (data.index.tz is None))
