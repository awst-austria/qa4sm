"""
Database-facing parts of the layer merge: the configuration model's gating, the
duplicate-run comparison, the copy path and the serializer's validation.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers

from api.views.dataset_configuration_view import ConfigurationSerializer
from api.views.validation_config_view import DatasetConfigSerializer
from validator.models import (
    Dataset,
    DatasetConfiguration,
    DatasetVersion,
    DataVariable,
    ValidationRun,
)
from validator.validation.validation import (
    _compare_merged_layers,
    apply_merged_naming,
    get_variable_naming,
)

User = get_user_model()

# fixture pks
ERA5_VERSION = 57
GLDAS_VERSION = 7
SWVL1, SWVL2, SWVL3 = 11, 24, 25
GLDAS_1, GLDAS_2 = 5, 6


def make_config(validation, version_id, variable_id, merged_ids=(),
                weighted=True):
    version = DatasetVersion.objects.get(pk=version_id)
    dataset = version.versions.first()
    config = DatasetConfiguration.objects.create(
        validation=validation,
        dataset=dataset,
        version=version,
        variable=DataVariable.objects.get(pk=variable_id),
        merge_weighted=weighted,
        is_spatial_reference=False,
        is_temporal_reference=False,
        is_scaling_reference=False)
    if merged_ids:
        config.merged_variables.set(merged_ids)
    return config


class TestMergeLayersDb(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

    def setUp(self):
        self.user = User.objects.create(username='merge-tester')
        self.run = ValidationRun.objects.create(user=self.user,
                                                start_time=timezone.now())

    # ---------------------------------------------------------------- gating

    def test_two_layers_is_a_merge(self):
        config = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        assert config.is_merged
        assert [v.short_name for v in config.merged_layers] == ['swvl1',
                                                                'swvl2']

    def test_a_single_layer_is_not_a_merge(self):
        config = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1])
        assert not config.is_merged
        assert config.merged_layers == []

    def test_no_selection_is_not_a_merge(self):
        config = make_config(self.run, ERA5_VERSION, SWVL1)
        assert not config.is_merged

    def test_merged_layers_are_ordered_by_depth(self):
        config = make_config(self.run, ERA5_VERSION, SWVL1,
                             [SWVL3, SWVL1, SWVL2])
        assert [v.short_name for v in config.merged_layers] == \
            ['swvl1', 'swvl2', 'swvl3']

    def test_a_non_whitelisted_dataset_degrades_to_no_merging(self):
        # the outer gate: even a stored selection is ignored off the whitelist
        config = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        config.dataset = Dataset.objects.get(short_name='ISMN')
        config.save()
        assert config.merged_layers == []

    def test_an_aggregate_in_the_selection_degrades_to_no_merging(self):
        # the inner gate. rzsm_1m spans the layers it would be merged with
        config = make_config(self.run, 73, 31, [31, 32])
        assert config.is_merged
        config.merged_variables.add(DataVariable.objects.get(pk=34))
        assert config.merged_layers == []

    # ------------------------------------------------------- naming (§8)

    def test_unmerged_naming_is_untouched(self):
        config = make_config(self.run, GLDAS_VERSION, GLDAS_1)
        variable = DataVariable.objects.get(pk=GLDAS_1)
        assert get_variable_naming(config) == (variable.pretty_name,
                                               variable.short_name,
                                               variable.unit)

    def test_unmerged_gldas_keeps_saying_kg_per_m2(self):
        # a single-layer GLDAS run still stores raw mass; relabelling it would
        # mislabel every existing GLDAS validation
        config = make_config(self.run, GLDAS_VERSION, GLDAS_1)
        assert get_variable_naming(config)[2] == 'kg/m²'

    def test_merged_naming_describes_the_depth(self):
        config = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        name, pretty_name, unit = get_variable_naming(config)
        # pretty_name is the slot qa4sm-reader actually plots, so the readable
        # depth range goes there and the column list stays as provenance
        assert pretty_name == '0-28 cm (merged)'
        assert name == 'swvl1+swvl2'
        assert unit == 'm³/m³'

    def test_merged_gldas_is_relabelled_volumetric(self):
        config = make_config(self.run, GLDAS_VERSION, GLDAS_1,
                             [GLDAS_1, GLDAS_2])
        _, pretty_name, unit = get_variable_naming(config)
        assert pretty_name == '0-40 cm (merged)'
        assert unit == 'm³/m³'

    # ------------------------------------------------------------ T1

    def test_identical_selections_compare_equal(self):
        a = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        b = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL2, SWVL1])
        assert _compare_merged_layers(a, b)

    def test_different_selections_compare_unequal(self):
        # the whole point of T1: without this the user is told they already ran
        # a validation they never ran
        a = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        b = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2, SWVL3])
        assert not _compare_merged_layers(a, b)

    def test_weighting_is_part_of_the_comparison(self):
        a = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        b = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2],
                        weighted=False)
        assert not _compare_merged_layers(a, b)

    def test_unmerged_configs_still_compare_equal(self):
        a = make_config(self.run, ERA5_VERSION, SWVL1)
        b = make_config(self.run, ERA5_VERSION, SWVL1)
        assert _compare_merged_layers(a, b)

    def test_no_selection_equals_a_single_leftover_layer(self):
        # neither is a merge, so they must not look different
        a = make_config(self.run, ERA5_VERSION, SWVL1)
        b = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1])
        assert _compare_merged_layers(a, b)

    def test_merged_and_unmerged_compare_unequal(self):
        a = make_config(self.run, ERA5_VERSION, SWVL1)
        b = make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        assert not _compare_merged_layers(a, b)


class TestOutputFileNaming(TestCase):
    """
    Result files are named after the columns pytesmo validated, so a merged run
    would advertise the one layer the merge happened to be written into.
    """
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

    def setUp(self):
        self.user = User.objects.create(username='merge-tester')
        self.run = ValidationRun.objects.create(user=self.user,
                                                start_time=timezone.now())

    def test_unmerged_names_are_untouched(self):
        make_config(self.run, GLDAS_VERSION, GLDAS_1)
        name = '0-ISMN.soil_moisture_with_1-GLDAS.SoilMoi0_10cm_inst.nc'
        assert apply_merged_naming(self.run, name) == name

    def test_merged_config_is_named_by_its_depth_range(self):
        make_config(self.run, GLDAS_VERSION, GLDAS_1, [GLDAS_1, GLDAS_2])
        assert apply_merged_naming(
            self.run,
            '0-ISMN.soil_moisture_with_1-GLDAS.SoilMoi0_10cm_inst.nc'
        ) == '0-ISMN.soil_moisture_with_1-GLDAS.0-40cm_merged.nc'

    def test_zarr_names_get_the_same_treatment(self):
        make_config(self.run, GLDAS_VERSION, GLDAS_1, [GLDAS_1, GLDAS_2])
        assert apply_merged_naming(
            self.run,
            '/out/3/0-ISMN.soil_moisture_with_1-GLDAS.SoilMoi0_10cm_inst.zarr'
        ) == '/out/3/0-ISMN.soil_moisture_with_1-GLDAS.0-40cm_merged.zarr'

    def test_spatial_names_get_the_same_treatment(self):
        make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        assert apply_merged_naming(
            self.run, '0-ISMN.soil_moisture_with_1-ERA5.swvl1_spatial_result.nc'
        ) == '0-ISMN.soil_moisture_with_1-ERA5.0-28cm_merged_spatial_result.nc'

    def test_only_the_merged_dataset_is_renamed(self):
        # ERA5 and ERA5-Land both name the column 'swvl1', so a substitution
        # keyed on the column alone would rename the wrong one too
        make_config(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        make_config(self.run, 62, 12)  # ERA5_LAND, not merged
        assert apply_merged_naming(
            self.run, '0-ERA5.swvl1_with_1-ERA5_LAND.swvl1.nc'
        ) == '0-ERA5.0-28cm_merged_with_1-ERA5_LAND.swvl1.nc'

    def test_gapped_pick_stays_filesystem_safe(self):
        make_config(self.run, GLDAS_VERSION, GLDAS_1, [GLDAS_1, 7])
        renamed = apply_merged_naming(
            self.run, '0-ISMN.soil_moisture_with_1-GLDAS.SoilMoi0_10cm_inst.nc')
        assert renamed == \
            '0-ISMN.soil_moisture_with_1-GLDAS.0-10_40-100cm_merged.nc'
        assert ' ' not in renamed and ',' not in renamed


class TestConfigurationSerializer(TestCase):
    """
    What the results summary and the validation lists are shown. These fields
    exist because resolving `variable` against the DataVariable table gives the
    wrong answer for a merged run.
    """
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

    def setUp(self):
        self.user = User.objects.create(username='merge-tester')
        self.run = ValidationRun.objects.create(user=self.user,
                                                start_time=timezone.now())

    def serialized(self, *args, **kwargs):
        return ConfigurationSerializer(make_config(*args, **kwargs)).data

    def test_unmerged_config_looks_exactly_as_before(self):
        data = self.serialized(self.run, GLDAS_VERSION, GLDAS_1)
        assert data['variable_unit'] == 'kg/m²'
        assert data['merged_layers'] == []
        assert data['merge_depth_label'] == ''

    def test_merged_gldas_reports_the_converted_unit(self):
        # the bug this was written for: the summary said kg/m² while the plot
        # beside it said m³/m³
        data = self.serialized(self.run, GLDAS_VERSION, GLDAS_1,
                               [GLDAS_1, GLDAS_2])
        assert data['variable_unit'] == 'm³/m³'

    def test_merged_volumetric_keeps_its_unit(self):
        data = self.serialized(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        assert data['variable_unit'] == 'm³/m³'

    def test_merged_layers_are_listed_with_their_depths(self):
        data = self.serialized(self.run, GLDAS_VERSION, GLDAS_1,
                               [GLDAS_1, GLDAS_2])
        assert [(l['short_name'], l['depth_from'], l['depth_to'])
                for l in data['merged_layers']] == [
            ('SoilMoi0_10cm_inst', 0.0, 0.1),
            ('SoilMoi10_40cm_inst', 0.1, 0.4)]

    def test_depth_label_spans_contiguous_picks(self):
        data = self.serialized(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2])
        assert data['merge_depth_label'] == '0-28 cm'

    def test_depth_label_lists_gapped_picks(self):
        data = self.serialized(self.run, GLDAS_VERSION, GLDAS_1,
                               [GLDAS_1, 7])
        assert data['merge_depth_label'] == '0-10, 40-100 cm'

    def test_weighting_flag_is_exposed(self):
        data = self.serialized(self.run, ERA5_VERSION, SWVL1, [SWVL1, SWVL2],
                               weighted=False)
        assert data['merge_weighted'] is False


class TestDatasetConfigSerializer(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']

    def payload(self, **overrides):
        data = {
            'dataset_id': DatasetVersion.objects.get(
                pk=ERA5_VERSION).versions.first().id,
            'version_id': ERA5_VERSION,
            'variable_id': SWVL3,
            'merged_variable_ids': [SWVL1, SWVL2],
            'merge_weighted': True,
            'basic_filters': [],
            'parametrised_filters': [],
            'is_spatial_reference': False,
            'is_temporal_reference': False,
            'is_scaling_reference': False,
        }
        data.update(overrides)
        return data

    def validated(self, **overrides):
        serializer = DatasetConfigSerializer(data=self.payload(**overrides))
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def test_output_variable_is_derived_from_the_selection(self):
        # posted variable_id is swvl3, which is not even in the merge set;
        # deriving it makes the invariant unbreakable rather than policed
        assert self.validated()['variable_id'] == SWVL1

    def test_derivation_picks_the_shallowest_layer(self):
        assert self.validated(
            merged_variable_ids=[SWVL3, SWVL2])['variable_id'] == SWVL2

    def test_a_single_layer_leaves_the_posted_variable_alone(self):
        result = self.validated(merged_variable_ids=[SWVL2])
        assert result['variable_id'] == SWVL3
        assert result['merged_variable_ids'] == []

    def test_absent_field_is_accepted(self):
        result = self.validated(merged_variable_ids=[])
        assert result['merged_variable_ids'] == []
        assert result['variable_id'] == SWVL3

    def test_a_variable_from_another_dataset_is_refused(self):
        # T4: ERA5-Land's swvl1 is pk 12 and its column is *also* named
        # 'swvl1', so without this the merge would quietly produce a
        # plausible-looking wrong series instead of failing
        with pytest.raises(serializers.ValidationError, match='do not belong'):
            self.validated(merged_variable_ids=[SWVL1, 12])

    def test_an_aggregate_is_refused(self):
        c3s_version = 73
        with pytest.raises(serializers.ValidationError,
                           match='not disjoint depth layers'):
            DatasetConfigSerializer(data=self.payload(
                dataset_id=DatasetVersion.objects.get(
                    pk=c3s_version).versions.first().id,
                version_id=c3s_version,
                variable_id=31,
                merged_variable_ids=[31, 34])).is_valid(raise_exception=True)

    def test_a_non_whitelisted_dataset_is_refused(self):
        ismn = Dataset.objects.get(short_name='ISMN')
        with pytest.raises(serializers.ValidationError,
                           match='not available for this dataset'):
            self.validated(dataset_id=ismn.id)
