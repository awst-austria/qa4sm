from django.test import TestCase
from django.test.utils import override_settings

from validator.models import Dataset
from validator.models import DataFilter
from validator.models import ParametrisedFilter
from auxiliary_functions import generate_default_validation_smos

from validator.validation.filters import setup_filtering, get_used_variables, check_normalized_bits_array
from validator.validation.readers import create_reader


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestValidation(TestCase):

    def setUp(self) -> None:
        run = generate_default_validation_smos()
        self.smos_dataset = Dataset.objects.get(short_name='SMOS_L3')
        run.reference_configuration.dataset = self.smos_dataset

        self.smos_filters = [
            DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'),
            DataFilter.objects.get(name='FIL_SMOSL3_RETRIEVAL')
        ]

        self.smos_reader = create_reader("SMOS_L3", "SMOSL3_DESC")

        self.smos_param_filters = [
            ParametrisedFilter(
                filter=DataFilter.objects.get(name='FIL_SMOSL3_RFI'),
                parameters=0.80,
                dataset_config=run.reference_configuration
            )
        ]

    def test_setup_filtering(self) -> None:
        setup_filtering(
            self.smos_reader,
            self.smos_filters,
            self.smos_param_filters,
            "SMOS_L3",
            "sm"
        )


def test_check_normalized_bits_array() -> None:
    pass
