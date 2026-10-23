import numpy as np
import pandas as pd
import pytest
from pytesmo.validation_framework.adapters import ColumnCombineAdapter

from validator.models import DataVariable
from validator.validation.adapters import LayerMergeAdapter
from validator.validation.depths import (
    depth_label,
    merge_coefficients,
    merged_labels,
    merged_unit,
)


def layer(short_name, depth_from, depth_to, unit='m³/m³',
          min_value=0.0, max_value=1.0):
    return DataVariable(short_name=short_name,
                        pretty_name=short_name,
                        unit=unit,
                        min_value=min_value,
                        max_value=max_value,
                        depth_from=depth_from,
                        depth_to=depth_to,
                        depth_kind=DataVariable.DepthKind.LAYER)


# the real fixture geometries and units
ERA5_1 = layer('swvl1', 0.00, 0.07)
ERA5_2 = layer('swvl2', 0.07, 0.28)

GLDAS_1 = layer('SoilMoi0_10cm_inst', 0.00, 0.10, unit='kg/m²', max_value=100)
GLDAS_2 = layer('SoilMoi10_40cm_inst', 0.10, 0.40, unit='kg/m²', max_value=300)
GLDAS_3 = layer('SoilMoi40_100cm_inst', 0.40, 1.00, unit='kg/m²',
                max_value=600)

RZSM_1 = layer('rzsm_1', 0.00, 0.10)
RZSM_2 = layer('rzsm_2', 0.10, 0.40)


class StubReader:
    """Minimal reader: returns whatever frame it was handed."""

    def __init__(self, frame):
        self.frame = frame

    def read(self, *args, **kwargs):
        return self.frame.copy()


def merge(frame, variables, weighted=True, adapter=LayerMergeAdapter):
    """Run a frame through the merge and return the output column."""
    columns, coefficients = merge_coefficients(variables, weighted=weighted)
    adapted = adapter(
        StubReader(frame),
        func=lambda row, c: float(np.dot(row, c)),
        func_kwargs={'c': coefficients},
        columns=columns,
        new_name=variables[0].short_name)
    return adapted.read()[variables[0].short_name]


def merged_values(frame, variables, **kwargs):
    """The merged column as a plain list, for comparison with approx()."""
    return merge(frame, variables, **kwargs).tolist()


class TestMergeCoefficients:

    def test_volumetric_whole_layers_give_thickness_weights(self):
        columns, coefficients = merge_coefficients([ERA5_1, ERA5_2])
        assert columns == ['swvl1', 'swvl2']
        # 0.07 and 0.21 of a 0.28 m column
        assert coefficients == pytest.approx([0.25, 0.75])
        assert sum(coefficients) == pytest.approx(1.0)

    def test_the_users_example(self):
        # C3S rzsm_1 + rzsm_2 over 0-40 cm -> 1/4 : 3/4
        _, coefficients = merge_coefficients([RZSM_1, RZSM_2])
        assert coefficients == pytest.approx([0.25, 0.75])

    def test_mass_folds_in_the_thickness_division(self):
        # for WHOLE layers ov == dz, so it cancels and every coefficient
        # collapses to the same 1/(rho_w * sum_ov): sum the masses, divide by
        # total depth times density. Asymmetric coefficients only show up once
        # a partial overlap breaks that cancellation (see the target test).
        _, coefficients = merge_coefficients([GLDAS_1, GLDAS_2])
        assert coefficients == pytest.approx([1 / 400, 1 / 400])
        assert coefficients == pytest.approx([1 / (1000 * 0.40)] * 2)
        # these do NOT sum to one, unlike the volumetric case
        assert sum(coefficients) == pytest.approx(0.005)

    def test_input_order_does_not_matter(self):
        _, forward = merge_coefficients([ERA5_1, ERA5_2])
        _, backward = merge_coefficients([ERA5_2, ERA5_1])
        assert forward == pytest.approx(backward)

    def test_unweighted_volumetric_is_a_plain_mean(self):
        _, coefficients = merge_coefficients([ERA5_1, ERA5_2], weighted=False)
        assert coefficients == pytest.approx([0.5, 0.5])

    def test_unweighted_mass_keeps_the_thickness_division(self):
        # an equal-weight mean of raw kg/m² is not a soil moisture at all,
        # so the per-layer unit fix has to survive turning weighting off
        _, coefficients = merge_coefficients([GLDAS_1, GLDAS_2],
                                             weighted=False)
        assert coefficients == pytest.approx([1 / (2 * 1000 * 0.10),
                                              1 / (2 * 1000 * 0.30)])

    def test_partial_overlap_against_an_external_target(self):
        # the phase-4 case: a 0-28 cm target from ERA5 cuts GLDAS layer 2
        _, coefficients = merge_coefficients([GLDAS_1, GLDAS_2],
                                             target=(0.00, 0.28))
        # ov/(rho_w * dz * sum_ov) = 0.10/(1000*0.10*0.28), 0.18/(1000*0.30*0.28)
        assert coefficients == pytest.approx([1 / 280, 3 / 1400])

    def test_single_layer_is_rejected(self):
        with pytest.raises(ValueError, match='at least two layers'):
            merge_coefficients([ERA5_1])

    def test_target_missing_the_layers_is_rejected(self):
        with pytest.raises(ValueError, match='do not overlap'):
            merge_coefficients([ERA5_1, ERA5_2], target=(2.00, 2.50))


class TestMergedSeries:
    """The numbers that actually come out of the adapter."""

    def test_uniform_volumetric_soil_survives_the_merge(self):
        frame = pd.DataFrame({'swvl1': [0.30] * 4, 'swvl2': [0.30] * 4},
                             index=pd.date_range('2020-01-01', periods=4))
        assert merged_values(frame, [ERA5_1, ERA5_2]) == pytest.approx([0.30] * 4)

    def test_uniform_mass_soil_comes_out_volumetric(self):
        # 30 and 90 kg/m² is theta = 0.30 in both layers
        frame = pd.DataFrame({'SoilMoi0_10cm_inst': [30.0] * 4,
                              'SoilMoi10_40cm_inst': [90.0] * 4},
                             index=pd.date_range('2020-01-01', periods=4))
        assert merged_values(frame, [GLDAS_1, GLDAS_2]) == pytest.approx([0.30] * 4)

    def test_gldas_and_era5_agree_on_the_same_soil(self):
        # the check that the whole scheme is right: same physical profile,
        # two different storage conventions, one answer
        index = pd.date_range('2020-01-01', periods=3)
        era5 = merged_values(
            pd.DataFrame({'swvl1': [0.22] * 3, 'swvl2': [0.22] * 3},
                         index=index), [ERA5_1, ERA5_2])
        gldas = merged_values(pd.DataFrame(
            {'SoilMoi0_10cm_inst': [0.22 * 1000 * 0.10] * 3,
             'SoilMoi10_40cm_inst': [0.22 * 1000 * 0.30] * 3},
            index=index), [GLDAS_1, GLDAS_2])
        assert era5 == pytest.approx([0.22] * 3)
        assert gldas == pytest.approx([0.22] * 3)

    def test_weighting_actually_changes_the_answer(self):
        # a wet thin top over a dry thick layer: the thick one must dominate
        frame = pd.DataFrame({'swvl1': [0.40], 'swvl2': [0.10]},
                             index=pd.date_range('2020-01-01', periods=1))
        weighted = merged_values(frame, [ERA5_1, ERA5_2])
        unweighted = merged_values(frame, [ERA5_1, ERA5_2], weighted=False)
        assert weighted == pytest.approx([0.25 * 0.40 + 0.75 * 0.10])
        assert unweighted == pytest.approx([0.25])
        assert weighted[0] < unweighted[0]

    def test_a_missing_layer_kills_the_timestamp(self):
        frame = pd.DataFrame(
            {'swvl1': [0.30, np.nan, 0.30, np.nan],
             'swvl2': [0.30, 0.30, np.nan, np.nan]},
            index=pd.date_range('2020-01-01', periods=4))
        result = merge(frame, [ERA5_1, ERA5_2])
        assert result.notna().tolist() == [True, False, False, False]

    def test_three_layers(self):
        frame = pd.DataFrame({'SoilMoi0_10cm_inst': [30.0],
                              'SoilMoi10_40cm_inst': [90.0],
                              'SoilMoi40_100cm_inst': [180.0]},
                             index=pd.date_range('2020-01-01', periods=1))
        # uniform theta = 0.30 across 0-100 cm
        assert merged_values(frame,
                             [GLDAS_1, GLDAS_2, GLDAS_3]) == pytest.approx([0.30])

    def test_non_contiguous_pick_is_permitted_and_sane(self):
        # 0-10 plus 40-100, skipping 10-40. Weights are 0.10 and 0.60 over the
        # 0.70 m actually selected - the gap is never filled in.
        frame = pd.DataFrame({'SoilMoi0_10cm_inst': [30.0],
                              'SoilMoi40_100cm_inst': [180.0]},
                             index=pd.date_range('2020-01-01', periods=1))
        assert merged_values(frame, [GLDAS_1, GLDAS_3]) == pytest.approx([0.30])

    def test_empty_frame_keeps_the_parent_contract(self):
        frame = pd.DataFrame({'swvl1': [], 'swvl2': []})
        assert 'swvl1' in merge(frame, [ERA5_1, ERA5_2]).name


class TestAgainstStockPytesmo:
    """
    The vectorised adapter must be a drop-in for stock ColumnCombineAdapter.
    Keeping this pinned means the local subclass stays A/B-testable against the
    upstream implementation, which is the reference.
    """

    @pytest.mark.parametrize('variables', [[ERA5_1, ERA5_2],
                                           [GLDAS_1, GLDAS_2]])
    def test_identical_output_including_nan_placement(self, variables):
        rng = np.random.default_rng(0)
        values = rng.random((50, 2)) * 100
        values[[3, 17, 42], 0] = np.nan
        values[[17, 30], 1] = np.nan
        frame = pd.DataFrame(
            {variables[0].short_name: values[:, 0],
             variables[1].short_name: values[:, 1]},
            index=pd.date_range('2020-01-01', periods=50))

        vectorised = merge(frame, variables, adapter=LayerMergeAdapter)
        stock = merge(frame, variables, adapter=ColumnCombineAdapter)

        pd.testing.assert_series_equal(vectorised, stock)


class TestLabels:

    def test_contiguous_pick_gets_a_span(self):
        assert depth_label([RZSM_1, RZSM_2]) == '0-40 cm'

    def test_era5_span(self):
        assert depth_label([ERA5_1, ERA5_2]) == '0-28 cm'

    def test_gapped_pick_is_described_by_its_members(self):
        assert depth_label([GLDAS_1, GLDAS_3]) == '0-10, 40-100 cm'

    def test_merged_labels(self):
        pretty, short = merged_labels([RZSM_1, RZSM_2])
        assert pretty == '0-40 cm (merged)'
        assert short == 'rzsm_1+rzsm_2'

    def test_volumetric_unit_is_untouched(self):
        assert merged_unit([ERA5_1, ERA5_2], 'm³/m³') == 'm³/m³'

    def test_mass_unit_becomes_volumetric(self):
        # the coefficients folded the conversion in, so the label must follow
        assert merged_unit([GLDAS_1, GLDAS_2], 'kg/m²') == 'm³/m³'
