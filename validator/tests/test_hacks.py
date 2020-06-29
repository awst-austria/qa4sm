'''
Because even (or especially?) hacks should be tested
'''

from os import path

from c3s_sm.interface import C3STs as c3s_read
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
        c3s_data_folder = path.join(Dataset.objects.get(short_name='C3S').storage_path, 'C3S_V201706/TCDR/063_images_to_ts/combined-daily')
        c3s_reader = c3s_read(c3s_data_folder)

        timezone_reader = TimezoneAdapter(c3s_reader)

        orig_data = c3s_reader.read_ts(-155.42, 19.78)
        data = timezone_reader.read_ts(-155.42, 19.78)
        self.assertTrue(np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue(not hasattr(data.index, 'tz') or data.index.tz is None)

        orig_data = c3s_reader.read(-155.42, 19.78)
        data = timezone_reader.read(-155.42, 19.78)
        self.assertTrue(np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue(data.index.tz is None)

        ismn_data_folder = path.join(Dataset.objects.get(short_name='ISMN').storage_path, 'ISMN_V20191211')
        ismn_reader = ISMN_Interface(ismn_data_folder)

        timezone_reader2 = TimezoneAdapter(ismn_reader)

        orig_data = ismn_reader.read_ts(0)
        data = timezone_reader2.read_ts(0)
        self.assertTrue(np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue(data.index.tz is None)
