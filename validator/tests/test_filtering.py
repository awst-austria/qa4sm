import numpy as np
import pandas as pd
import pytest
from django.test import TestCase
from django.test.utils import override_settings
import django

from validator.admin import User
from validator.models import DataFilter, DataVariable
from pytesmo.validation_framework.adapters import AdvancedMaskingAdapter

from validator.models import ParametrisedFilter
from validator.tests.auxiliary_functions import generate_default_validation_smos, generate_default_validation_smos_l2

from validator.validation.filters import setup_filtering, get_used_variables, check_normalized_bits_array
from validator.validation.readers import create_reader


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestValidation(TestCase):
    databases = '__all__'
    allow_database_queries = True
    fixtures = ['variables', 'versions', 'datasets', 'filters']

    def setUp(self) -> None:
        self.run = generate_default_validation_smos()
        self.user_data = {
            'username': 'testuser',
            'password': 'secret',
            'email': 'noreply@awst.at'
        }

        try:
            self.testuser = User.objects.get(username=self.user_data['username'])
        except User.DoesNotExist:
            self.testuser = User.objects.create_user(**self.user_data)

        self.run.user = self.testuser

        for config in self.run.dataset_configurations.all():
            if config == self.run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
            else:
                self.smos_config = config
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.filters.add(DataFilter.objects.get(name='FIL_SMOSL3_EXTERNAL'))

            config.save()

        self.rfi_theshold = 0.01  # needs to be low as testdata have low values
        self.chi2_theshold = 0.05  # needs to be low as testdata have low values
        pfilter = ParametrisedFilter(
            filter=DataFilter.objects.get(name="FIL_SMOSL3_RFI"),
            parameters=self.rfi_theshold,
            dataset_config=self.smos_config
        )
        pfilter.save()
        pfilter = ParametrisedFilter(
            filter=DataFilter.objects.get(name="FIL_SMOSL2_CHI2P"),
            parameters=self.chi2_theshold,
            dataset_config=self.smos_config
        )
        pfilter.save()

        self.smos_reader = create_reader(
            self.smos_config.dataset,
            self.smos_config.version
        )

        # Create a custom DataFrame to test the functions
        # take real data
        data = self.smos_reader.read(542803)
        data["Soil_Moisture"] = data.apply(
            lambda row: np.random.uniform(0, 1) if ~np.isnan(row["Ratio_RFI"]) else np.nan, axis=1
        )

        def _read():
            return data

        setattr(self.smos_reader, "read", _read)

        self.filtered_reader, self.read_name, self.read_kwargs = setup_filtering(
            self.smos_reader,
            self.smos_config.filters.all(),
            ParametrisedFilter.objects.filter(dataset_config_id=self.smos_config.id),
            self.smos_config.version,
            self.smos_config.variable,
        )

    def test_setup_filtering(self) -> None:
        # check that the function outputs the correct objects
        f_list_should = [
            ('Ratio_RFI', '<=', self.rfi_theshold),
            ('Chi_2', '>=', self.chi2_theshold),
            ('Soil_Moisture', '>=', 0.0),
            ('Soil_Moisture', '<=', 1.0),
            ('Science_Flags', check_normalized_bits_array, [[24], [25]])
        ]
        assert isinstance(self.filtered_reader, AdvancedMaskingAdapter)
        assert self.filtered_reader.filter_list == f_list_should

        assert self.read_name == 'read'
        assert not self.read_kwargs

        out_data = self.filtered_reader.read()
        # check that the reader filters the data correctly
        assert list(out_data.columns) == [
            'Soil_Moisture',
            'Soil_Moisture_Dqx',
            'Chi_2',
            'Science_Flags',
            'Rfi_Prob',
            'Mean_Acq_Time_Days',
            'Mean_Acq_Time_Seconds',
            'Ratio_RFI',
            'Optical_Thickness_Nad'
        ]
        assert self.smos_reader.read().Ratio_RFI.count() > out_data.Ratio_RFI.count()
        # assert Rfi threshold works
        assert (out_data.Ratio_RFI.values < self.rfi_theshold).all()

        # assert the bit function works on data
        def return_index(x, ind):
            try:
                return str(bin(x)).split('b')[1][ind]
            except IndexError:
                return "0"
        df_filtered = out_data.Science_Flags.apply(
            lambda x: return_index(x, -26)
        )
        df_unfiltered = self.smos_reader.read().Science_Flags.apply(
            lambda x: return_index(x, -26)
        )
        # assert one gets filtered, the other doesn't
        assert (df_filtered == "0").all() \
               and not (df_unfiltered == "0").all()

    def test_reading_ColumnCombineAdapter(self) -> None:
        # test that the pytesmo.validation_framework.adapters.ColumnCombineAdapter
        # works properly for SMOS L2
        self.run = generate_default_validation_smos_l2()
        self.user_data = {
            'username': 'testuser',
            'password': 'secret',
            'email': 'noreply@awst.at'
        }

        try:
            self.testuser = User.objects.get(username=self.user_data['username'])
        except User.DoesNotExist:
            self.testuser = User.objects.create_user(**self.user_data)

        self.run.user = self.testuser
        for config in self.run.dataset_configurations.all():
            if config == self.run.reference_configuration:
                config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
            else:
                self.smos_config = config
                config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.filters.add(DataFilter.objects.get(name='FIL_SMOSL2_RFI_high_confidence'))

            config.save()

        self.smos_reader = create_reader(
            self.smos_config.dataset,
            self.smos_config.version
        )

        # Create a custom DataFrame to test the functions
        # take real data
        data = self.smos_reader.read(9129961)

        def _read():
            return data

        setattr(self.smos_reader, "read", _read)

        self.filtered_reader, self.read_name, self.read_kwargs = setup_filtering(
            self.smos_reader,
            self.smos_config.filters.all(),
            ParametrisedFilter.objects.filter(dataset_config_id=self.smos_config.id),
            self.smos_config.version,
            self.smos_config.variable,
        )

        filtered = self.filtered_reader.read()

        # Check that the 'COMBINED_RFI' field has been created
        columns_should = ['Soil_Moisture', 'Soil_Moisture_DQX', 'Chi_2', 'RFI_Prob',
                          'Science_Flags', 'Days', 'Seconds', 'N_RFI_X', 'N_RFI_Y',
                          'M_AVA0', 'Processing_Flags', 'Confidence_Flags', 'COMBINED_RFI']
        data_should = [[0.366221, 0.071858, 19.7451, 0.02, 542114818.0, 3.291840e+17,
                       57914.0, 5.0, 2.0, 78.0, 4.0, 128.0, 0.089744]]
        index_should = [pd.datetime(2010, 6, 7, 15, 18, 27)]

        filtered_should = pd.DataFrame(data=data_should, index=index_should, columns=columns_should)

        # check 'COMBINED_RFI' formula COMBINED_RFI = (N_RFI_X + N_RFI_Y) / M_AVA0
        np.testing.assert_array_equal(filtered['COMBINED_RFI'].values,
                                       ((filtered['N_RFI_X'] + filtered['N_RFI_Y']) / filtered['M_AVA0']).values)
        pd.testing.assert_frame_equal(filtered, filtered_should)

    def test_get_used_variables(self) -> None:
        # provide a few filters to test
        tested_data = [
            ("FIL_ISMN_GOOD", "ISMN_soil_moisture", "soil_moisture_flag", DataFilter),
            ("FIL_C3S_MODE_ASC", "C3S_sm", "mode", DataFilter),
            ("FIL_ASCAT_METOP_A", "ASCAT_sm", "sat_id", DataFilter),
            ("FIL_ERA5_TEMP_UNFROZEN", "ERA5_sm", "stl1", DataFilter),
            ("FIL_SMOSL3_STRONG_TOPO_MANDATORY", "SMOSL3_sm", "Science_Flags", DataFilter),
            ("FIL_SMOSL3_RFI", "SMOSL3_sm", "Ratio_RFI", ParametrisedFilter),
            ("FIL_SMOSL2_RFI_good_confidence", "SMOSL2_sm", ["RFI_Prob", "N_RFI_X", "N_RFI_Y", "M_AVA0"], DataFilter),
            ("FIL_SMOSL2_CHI2P", "SMOSL2_sm", "Chi_2", ParametrisedFilter),
            ("FIL_SMOSL2_OW", "SMOSL2_sm", "Science_Flags", DataFilter)
        ]
        for filtername, sm_variable, filter_variable_should, model in tested_data:
            try:
                filters = [model.objects.get(name=filtername), ]
            except django.core.exceptions.FieldError:
                datafilter = DataFilter.objects.get(name=filtername)
                filters = [model.objects.get(filter=datafilter), ]

            variable = DataVariable.objects.get(short_name=sm_variable)
            used_variables = get_used_variables(
                filters, dataset=None, variable=variable
            )
            used_variables_should = [variable.pretty_name]
            if isinstance(filter_variable_should, list):
                used_variables_should.extend(filter_variable_should)
            else:
                used_variables_should.append(filter_variable_should)

            assert used_variables == used_variables_should


bits_list = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

bits_tests = [
    (bits_list, [[3]], np.array([True, True, True, True, True, True, True, True, False, False])),
    (bits_list, [[0], [1]], np.array([True, False, False, False, True, False, False, False, True, False])),
    (bits_list, [[0, 1]], np.array([True, True, True, False, True, True, True, False, True, True])),
    (bits_list, [[3], [0, 1]], np.array([True, True, True, False, True, True, True, False, False, False])),
]

test_names = [
    "single",
    "or",
    "and",
    "and_or"
]


@pytest.mark.parametrize(
    "input_list, input_indices, expected", bits_tests, ids=test_names
)
def test_check_normalized_bits_array(input_list, input_indices, expected) -> None:
    result = check_normalized_bits_array(input_list, input_indices)

    np.testing.assert_array_equal(
        result, expected
    )
