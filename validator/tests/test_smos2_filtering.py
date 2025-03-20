import numpy as np
import pandas as pd
from django.test import TestCase
from django.test.utils import override_settings

from validator.admin import User
from validator.models import DataFilter

from validator.models import ParametrisedFilter
from validator.tests.auxiliary_functions import \
    generate_default_validation_smos_l2

from validator.validation.filters import setup_filtering
from validator.validation.readers import create_reader


# TODO: Check
@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestSmos2Filtering(TestCase):
    databases = '__all__'
    allow_database_queries = True
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

    def setUp(self) -> None:
        # test that the pytesmo.validation_framework.adapters
        # .ColumnCombineAdapter
        # works properly for SMOS L2
        self.run = generate_default_validation_smos_l2(sbpca=True)
        self.user_data = {
            'username': 'testuser',
            'password': 'secret',
            'email': 'noreply@awst.at'
        }

        try:
            self.testuser = User.objects.get(
                username=self.user_data['username'])
        except User.DoesNotExist:
            self.testuser = User.objects.create_user(**self.user_data)

        self.run.user = self.testuser
        for config in self.run.dataset_configurations.all():
            if config == self.run.spatial_reference_configuration:
                config.filters.add(
                    DataFilter.objects.get(name='FIL_ISMN_GOOD'))
            else:
                self.smos_config = config
                config.filters.add(
                    DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.filters.add(DataFilter.objects.get(
                    name='FIL_SMOSL2_RFI_high_confidence'))

            config.save()
        # todo
        self.smos_reader = create_reader(
            self.smos_config.dataset,
            self.smos_config.version
        )

        # Create a custom DataFrame to test the functions
        # take real data
        data = self.smos_reader.read(9138158)

        def _read():
            return data

        setattr(self.smos_reader, "read", _read)

        self.filtered_reader, self.read_name, self.read_kwargs = (
            setup_filtering(
            self.smos_reader,
            self.smos_config.filters.all(),
            ParametrisedFilter.objects.filter(
                dataset_config_id=self.smos_config.id),
            self.smos_config.version,
            self.smos_config.variable,
        ))

    def test_reading_ColumnCombineAdapter(self) -> None:
        filtered = self.filtered_reader.read()

        # Check that the 'COMBINED_RFI' field has been created
        index_should = ['Soil_Moisture', 'Chi_2_P', 'RFI_Prob',
                        'Science_Flags', 'Days',
                        'Seconds', 'N_RFI_X', 'N_RFI_Y', 'M_AVA0', 'Overpass',
                        'COMBINED_RFI']
        data_mean_should = np.array(
            [1.91801946e-01, 4.79034721e-01, 7.56410237e-03, 5.48010184e+08,
             5.65984246e+17, 5.92144872e+04, 8.97435897e-01, 5.12820513e-01,
             1.41410256e+02, 1.53846154e+00, 9.87404715e-03]
        )
        filtered_mean_should = pd.Series(data=data_mean_should,
                                         index=index_should)

        # check 'COMBINED_RFI' formula COMBINED_RFI = (N_RFI_X + N_RFI_Y) /
        # M_AVA0
        np.testing.assert_array_equal(filtered['COMBINED_RFI'].values,
                                      ((filtered['N_RFI_X'] + filtered[
                                          'N_RFI_Y']) / filtered[
                                           'M_AVA0']).values)

        assert (filtered.COMBINED_RFI > .1).sum() == 0
        assert (filtered.RFI_Prob > .1).sum() == 0
        assert len(filtered.index) == 39
        pd.testing.assert_series_equal(filtered.mean(), filtered_mean_should)
