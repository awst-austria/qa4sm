from django.test import TestCase
from django.test.utils import override_settings

from validator.models import DataFilter
from validator.models import ParametrisedFilter
from validator.tests.auxiliary_functions import generate_default_validation_smos

from validator.validation.filters import setup_filtering, get_used_variables, check_normalized_bits_array
from validator.validation.readers import create_reader


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestValidation(TestCase):

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


def test_check_normalized_bits_array() -> None:
    pass
