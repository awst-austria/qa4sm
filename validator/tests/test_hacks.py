'''
Because even (or especially?) hacks should be tested
'''

from os import path

from c3s_sm.interface import C3STs as c3s_read

from django.test import TestCase

import numpy as np
from validator.hacks import TimezoneAdapter
from ismn.interface import ISMN_Interface


class TestHacks(TestCase):

    def test_timezone_adapter(self):
        from valentina.settings import DATA_FOLDER

        c3s_data_folder = path.join(DATA_FOLDER, 'C3S/C3S_V201706/TCDR/063_images_to_ts/combined-daily')
        c3s_reader = c3s_read(c3s_data_folder)

        timezone_reader = TimezoneAdapter(c3s_reader)

        orig_data = c3s_reader.read_ts(567036)
        data = timezone_reader.read_ts(567036)
        self.assertTrue(np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue(data.index.tz is None)

        orig_data = c3s_reader.read(567036)
        data = timezone_reader.read(567036)
        self.assertTrue(np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue(data.index.tz is None)

        ismn_data_folder = path.join(DATA_FOLDER, 'ISMN/ISMN_V20180830_GLOBAL')
        ismn_reader = ISMN_Interface(ismn_data_folder)

        timezone_reader2 = TimezoneAdapter(ismn_reader)

        orig_data = ismn_reader.read_ts(0)
        data = timezone_reader2.read_ts(0)
        self.assertTrue(np.array_equal(orig_data.index.values, data.index.values))
        self.assertTrue(data.index.tz is None)
