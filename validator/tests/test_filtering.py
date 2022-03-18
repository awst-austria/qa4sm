from django.test import TestCase
from django.test.utils import override_settings
import django

from validator.admin import User
from validator.models import DataFilter, DataVariable

from validator.models import ParametrisedFilter
from validator.tests.auxiliary_functions import generate_default_validation_smos

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
                config.filters.add(DataFilter.objects.get(name='FIL_SMOSL3_RETRIEVAL'))

            config.save()

        pfilter = ParametrisedFilter(
            filter=DataFilter.objects.get(name="FIL_SMOSL3_RFI"),
            parameters=0.8,
            dataset_config=self.smos_config
        )
        pfilter.save()

        self.smos_reader = create_reader(
            self.smos_config.dataset,
            self.smos_config.version
        )

    def test_setup_filtering(self) -> None:
        filtered_reader, read_name, read_kwargs = setup_filtering(
            self.smos_reader,
            self.smos_config.filters.all(),
            ParametrisedFilter.objects.filter(dataset_config_id=self.smos_config.id),
            self.smos_config.version,
            self.smos_config.variable,
        )
        f_list_should = [
            ('Rfi_Prob', '<=', 0.8),
            ('Soil_Moisture', '>=', 0.0),
            ('Soil_Moisture', '<=', 1.0),
            ('Science_Flags', check_normalized_bits_array, [[20], [21], [22], [23]])
        ]
        assert filtered_reader.filter_list == f_list_should

        assert read_name == 'read'
        assert not read_kwargs

    def test_get_used_variables(self) -> None:
        # provide a few filters to test
        tested_data = [
            ("FIL_ISMN_GOOD", "ISMN_soil_moisture", "soil_moisture_flag", DataFilter),
            ("FIL_C3S_MODE_ASC", "C3S_sm", "mode", DataFilter),
            ("FIL_ASCAT_METOP_A", "ASCAT_sm", "sat_id", DataFilter),
            ("FIL_ERA5_TEMP_UNFROZEN", "ERA5_sm", "stl1", DataFilter),
            ("FIL_SMOSL3_STRONG_TOPO", "SMOSL3_sm", "Science_Flags", DataFilter),
            ("FIL_SMOSL3_RFI", "SMOSL3_sm", "Rfi_Prob", ParametrisedFilter),
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
            used_variables_should = [variable.pretty_name, filter_variable_should]

            assert used_variables == used_variables_should

# bits_tests = [
#     ('', [[3]], ),
# ]
# def test_check_normalized_bits_array() -> None:
#     pass
