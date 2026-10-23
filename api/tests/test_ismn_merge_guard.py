from django.test import TestCase
from rest_framework import serializers

from api.views.validation_config_view import ValidationConfigurationSerializer
from validator.models import DataFilter, ValidationRun


class TestIsmnMergeValidationType(TestCase):
    """ISMN sensor merging is only accepted for temporal validations."""
    fixtures = ['filters']

    def attrs(self, val_type, filter_name=None):
        parametrised_filters = []
        if filter_name is not None:
            parametrised_filters.append({
                'id': DataFilter.objects.get(name=filter_name).id,
                'parameters': '0.1,0.1'})
        return {
            'dataset_configs': [{
                'is_spatial_reference': True,
                'is_temporal_reference': True,
                'is_scaling_reference': False,
                'parametrised_filters': parametrised_filters,
            }],
            'scaling_method': 'none',
            'anomalies_method': 'none',
            'val_type': val_type,
        }

    def validate(self, attrs):
        return ValidationConfigurationSerializer().validate(attrs)

    def test_merging_with_temporal_validation_is_accepted(self):
        self.validate(self.attrs(ValidationRun.VAL_TYPE_TEMPORAL,
                                 'FIL_ISMN_TOLERANCES'))

    def test_merging_with_spatial_or_both_is_rejected(self):
        for val_type in [ValidationRun.VAL_TYPE_SPATIAL,
                         ValidationRun.VAL_TYPE_BOTH]:
            with self.assertRaisesMessage(serializers.ValidationError,
                                          'only available for temporal'):
                self.validate(self.attrs(val_type, 'FIL_ISMN_TOLERANCES'))

    def test_spatial_without_merging_is_accepted(self):
        self.validate(self.attrs(ValidationRun.VAL_TYPE_SPATIAL,
                                 'FIL_ISMN_DEPTH'))
