import pytest
from django.db.utils import IntegrityError
from django.test import TestCase

from validator.models import DataVariable
from validator.validation.depths import (
    DEPTH_TOL,
    is_contiguous,
    layers_to_range,
    overlap,
    range_to_layers,
    sort_by_depth,
)


def layer(short_name, depth_from, depth_to,
          kind=DataVariable.DepthKind.LAYER, unit='m³/m³'):
    """An unsaved DataVariable — these functions never touch the database."""
    return DataVariable(short_name=short_name,
                        pretty_name=short_name,
                        unit=unit,
                        depth_from=depth_from,
                        depth_to=depth_to,
                        depth_kind=kind)


# the real fixture geometries, so the tests fail if the depths ever drift
ERA5 = [layer('swvl1', 0.00, 0.07), layer('swvl2', 0.07, 0.28),
        layer('swvl3', 0.28, 1.00), layer('swvl4', 1.00, 2.89)]

GLDAS = [layer('SoilMoi0_10cm_inst', 0.00, 0.10, unit='kg/m²'),
         layer('SoilMoi10_40cm_inst', 0.10, 0.40, unit='kg/m²'),
         layer('SoilMoi40_100cm_inst', 0.40, 1.00, unit='kg/m²'),
         layer('SoilMoi100_200cm_inst', 1.00, 2.00, unit='kg/m²')]

C3S_RZSM = [layer('rzsm_1', 0.00, 0.10), layer('rzsm_2', 0.10, 0.40),
            layer('rzsm_3', 0.40, 1.00), layer('rzsm_4', 1.00, 2.00),
            layer('rzsm_1m', 0.00, 1.00,
                  kind=DataVariable.DepthKind.AGGREGATE)]


class TestLayersToRange:

    def test_empty_selection(self):
        assert layers_to_range([]) is None

    def test_single_layer(self):
        assert layers_to_range([ERA5[0]]) == (0.00, 0.07)

    def test_the_users_example(self):
        # C3S rzsm_1 + rzsm_2 -> 0-40 cm, the case that motivated the feature
        assert layers_to_range(C3S_RZSM[:2]) == (0.00, 0.40)

    def test_first_two_layers_differ_between_datasets(self):
        # the trap: "the first two layers of each" is NOT the same depth
        assert layers_to_range(ERA5[:2]) == (0.00, 0.28)
        assert layers_to_range(C3S_RZSM[:2]) == (0.00, 0.40)

    def test_order_of_input_does_not_matter(self):
        assert layers_to_range(list(reversed(ERA5))) == (0.00, 2.89)

    def test_variable_without_depth_is_rejected(self):
        swi = layer('SWI_005', None, None, kind=DataVariable.DepthKind.NA)
        with pytest.raises(ValueError, match='no depth information'):
            layers_to_range([swi])

    def test_inverted_bounds_are_rejected(self):
        with pytest.raises(ValueError, match='depth_to <= depth_from'):
            layers_to_range([layer('broken', 0.40, 0.10)])


class TestIsContiguous:

    def test_single_layer_is_trivially_contiguous(self):
        assert is_contiguous([ERA5[0]]) is True

    def test_empty_is_trivially_contiguous(self):
        assert is_contiguous([]) is True

    def test_adjacent_layers(self):
        assert is_contiguous(ERA5[:2]) is True
        assert is_contiguous(GLDAS) is True

    def test_gap_is_detected(self):
        # GLDAS 0-10 and 40-100, skipping 10-40. This is a permitted selection;
        # is_contiguous only reports that "0-100 cm" would be a misleading
        # label for it, since 30 cm of that span contributed nothing
        assert is_contiguous([GLDAS[0], GLDAS[2]]) is False

    def test_non_contiguous_selection_is_still_usable(self):
        # the user is responsible for their own settings: a gapped pick must
        # not be blocked, and its merged value stays well defined because the
        # weights are the picked layers' own thicknesses, not the whole span
        picked = [GLDAS[0], GLDAS[2]]
        assert layers_to_range(picked) == (0.00, 1.00)
        total = sum(v.thickness for v in picked)
        assert total == pytest.approx(0.70)          # NOT 1.00 — no gap filling
        weights = [v.thickness / total for v in picked]
        assert weights == pytest.approx([1 / 7, 6 / 7])

    def test_unordered_input_still_detected_as_contiguous(self):
        assert is_contiguous([ERA5[1], ERA5[0]]) is True

    def test_overlapping_layers_are_not_contiguous(self):
        # rzsm_1 (0-10) and the rzsm_1m aggregate (0-1m) overlap
        assert is_contiguous([C3S_RZSM[0], C3S_RZSM[4]]) is False

    def test_float_boundaries_do_not_trip_the_tolerance(self):
        # 0.07 and 0.28 are not exactly representable in binary floating point
        assert is_contiguous([ERA5[0], ERA5[1], ERA5[2]]) is True


class TestOverlap:

    def test_layer_fully_inside_target_gives_full_thickness(self):
        assert overlap(GLDAS[0], 0.00, 0.28) == pytest.approx(0.10)

    def test_layer_cut_by_target(self):
        # the case that motivated overlap weighting: GLDAS 10-40 cm against a
        # 0-28 cm target contributes only 18 of its 30 cm
        assert overlap(GLDAS[1], 0.00, 0.28) == pytest.approx(0.18)

    def test_layer_outside_target(self):
        assert overlap(GLDAS[3], 0.00, 0.28) == 0.0

    def test_target_inside_a_single_layer(self):
        assert overlap(GLDAS[1], 0.15, 0.25) == pytest.approx(0.10)

    def test_touching_but_not_overlapping(self):
        assert overlap(GLDAS[1], 0.00, 0.10) == 0.0


class TestRangeToLayers:

    def test_era5_target_lands_on_its_own_boundaries(self):
        result = range_to_layers(0.00, 0.28, ERA5)
        assert [v.short_name for v, _ in result] == ['swvl1', 'swvl2']
        # whole layers, so the overlaps are just the thicknesses -> 1/4 : 3/4
        overlaps = [ov for _, ov in result]
        assert overlaps == pytest.approx([0.07, 0.21])
        total = sum(overlaps)
        assert [ov / total for ov in overlaps] == pytest.approx([0.25, 0.75])

    def test_same_target_cuts_a_gldas_layer_in_half(self):
        result = range_to_layers(0.00, 0.28, GLDAS)
        assert [v.short_name for v, _ in result] == ['SoilMoi0_10cm_inst',
                                                     'SoilMoi10_40cm_inst']
        assert [ov for _, ov in result] == pytest.approx([0.10, 0.18])
        # and the fraction of each layer included, which is the weight that
        # will be applied to the raw kg/m² values
        fractions = [ov / v.thickness for v, ov in result]
        assert fractions == pytest.approx([1.00, 0.60])

    def test_aggregate_is_excluded(self):
        # rzsm_1m spans 0-1 m and would double-count rzsm_1..3
        result = range_to_layers(0.00, 1.00, C3S_RZSM)
        assert 'rzsm_1m' not in [v.short_name for v, _ in result]
        assert [v.short_name for v, _ in result] == ['rzsm_1', 'rzsm_2',
                                                     'rzsm_3']

    def test_variables_without_depth_are_excluded(self):
        swi = [layer('SWI_005', None, None, kind=DataVariable.DepthKind.NA),
               layer('SWI_040', None, None, kind=DataVariable.DepthKind.NA)]
        assert range_to_layers(0.00, 0.40, swi) == []

    def test_result_is_ordered_shallowest_first(self):
        result = range_to_layers(0.00, 2.00, list(reversed(GLDAS)))
        assert [v.short_name for v, _ in result] == [
            'SoilMoi0_10cm_inst', 'SoilMoi10_40cm_inst',
            'SoilMoi40_100cm_inst', 'SoilMoi100_200cm_inst']

    def test_target_below_all_layers_gives_nothing(self):
        assert range_to_layers(3.00, 4.00, ERA5) == []

    def test_inverted_target_is_rejected(self):
        with pytest.raises(ValueError, match='depth_to must be greater'):
            range_to_layers(0.40, 0.10, ERA5)

    def test_round_trips_with_layers_to_range(self):
        # picking whole layers and then asking which layers cover that range
        # must give back exactly what was picked, at full thickness
        picked = C3S_RZSM[:2]
        depth_from, depth_to = layers_to_range(picked)
        result = range_to_layers(depth_from, depth_to, C3S_RZSM)
        assert [v.short_name for v, _ in result] == ['rzsm_1', 'rzsm_2']
        assert [ov for _, ov in result] == pytest.approx(
            [v.thickness for v in picked])


class TestSortByDepth:

    def test_sorts_shallowest_first(self):
        assert [v.short_name for v in sort_by_depth(list(reversed(ERA5)))] == \
            ['swvl1', 'swvl2', 'swvl3', 'swvl4']

    def test_ties_on_depth_from_break_on_depth_to(self):
        # rzsm_1 (0-0.10) and rzsm_1m (0-1.00) share a depth_from
        ordered = sort_by_depth([C3S_RZSM[4], C3S_RZSM[0]])
        assert [v.short_name for v in ordered] == ['rzsm_1', 'rzsm_1m']


class TestDataVariableDepthFields(TestCase):

    def test_thickness(self):
        assert layer('swvl2', 0.07, 0.28).thickness == pytest.approx(0.21)

    def test_thickness_is_none_without_depths(self):
        assert layer('SWI_005', None, None).thickness is None

    def test_is_mergeable_layer(self):
        assert layer('swvl1', 0.00, 0.07).is_mergeable_layer is True

    def test_aggregate_is_not_mergeable(self):
        aggregate = layer('rzsm_1m', 0.00, 1.00,
                          kind=DataVariable.DepthKind.AGGREGATE)
        assert aggregate.is_mergeable_layer is False

    def test_undeclared_variable_is_not_mergeable(self):
        assert layer('sm', None, None,
                     kind=DataVariable.DepthKind.NA).is_mergeable_layer is False

    def test_existing_variables_default_to_not_mergeable(self):
        # every pre-existing row must stay out of merging without being touched
        plain = DataVariable.objects.create(short_name='sm',
                                            pretty_name='sm',
                                            help_text='')
        assert plain.depth_kind == DataVariable.DepthKind.NA
        assert plain.depth_from is None
        assert plain.is_mergeable_layer is False

    def test_declaring_a_kind_without_depths_is_refused(self):
        # guards the inverse mistake to the one depth_kind exists to prevent:
        # a half-filled row that claims to be a layer
        with pytest.raises(IntegrityError):
            DataVariable.objects.create(
                short_name='swvl1', pretty_name='swvl1', help_text='',
                depth_kind=DataVariable.DepthKind.LAYER)

    def test_declaring_a_kind_with_depths_is_allowed(self):
        saved = DataVariable.objects.create(
            short_name='swvl1', pretty_name='swvl1', help_text='',
            depth_from=0.0, depth_to=0.07,
            depth_kind=DataVariable.DepthKind.LAYER)
        assert saved.is_mergeable_layer is True
