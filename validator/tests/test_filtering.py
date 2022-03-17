from django.test import TestCase
from django.test.utils import override_settings

from validator.models import DataFilter, DataVariable
from validator.models import ParametrisedFilter
from validator.tests.auxiliary_functions import generate_default_validation_smos

from validator.validation.filters import setup_filtering, get_used_variables, check_normalized_bits_array
from validator.validation.readers import create_reader

import pytest


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestValidation(TestCase):
    databases = '__all__'
    allow_database_queries = True
    fixtures = ['variables', 'versions', 'datasets', 'filters']

    def setUp(self) -> None:
        self.run = generate_default_validation_smos()
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
        setup_filtering(
            self.smos_reader,
            self.smos_config.filters,
            self.smos_config.parametrised_filters,
            self.smos_config.version,
            self.smos_config.variable,
        )


tested_data = [
    ("FIL_ISMN_GOOD", "ISMN_soil_moisture", "soil_moisture_flag"),
    ("FIL_C3S_MODE_ASC", "C3S_sm", "flag"),
    ("FIL_ASCAT_METOP_A", "ASCAT_sm", "sat_id"),
    ("FIL_ERA5_TEMP_UNFROZEN", "ERA5_sm", "t"),
    ("FIL_SMOSL3_STRONG_TOPO", "SMOSL3_sm", "Science_Flags"),
    ("FIL_SMOSL3_RFI", "SMOSL3_sm", "Rfi_Prob"),
]
tested_filters = [
    "ISMN_good", "C3S_mode", "ASCAT_satellite",
    "ERA_frozen", "SMOSL3_flag", "SMOSL3_parametrised"
]


@pytest.mark.parametrize(
    "filtername, sm_variable, filter_variable_should",
    tested_data, ids=tested_filters
)
@pytest.mark.django_db
def test_get_used_variables(filtername, sm_variable, filter_variable_should) -> None:
    filters = [DataFilter.objects.get(name=filtername), ]
    variable = DataVariable.objects.get(short_name=sm_variable)
    used_variables = get_used_variables(
        filters, dataset=None, variable=variable
    )
    print(used_variables)

def test_check_normalized_bits_array() -> None:
    pass
