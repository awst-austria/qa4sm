"""
BIAS is reported as mean(candidate) - mean(reference), see
CandidateMinusReferencePairwiseMetrics, and runs computed before that change
are marked by ValidationRun.bias_candidate_minus_reference = False.
"""
from datetime import datetime

import numpy as np
import pandas as pd
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone
from pytesmo.time_series.grouping import TsDistributor, YearlessDatetime
from pytesmo.validation_framework.metric_calculators import \
    PairwiseIntercomparisonMetrics
from pytesmo.validation_framework.metric_calculators_adapters import \
    SubsetsMetricsAdapter

from validator.validation.adapters import (
    CandidateMinusReferencePairwiseMetrics, StabilityMetricsAdapter)

GPI = (0, 0.0, 0.0)
FLIPPED = {"BIAS", "BIAS_ci_lower", "BIAS_ci_upper"}


def _data(n=3 * 365, seed=1):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2015-01-01", periods=n, freq="D")
    ref = 0.25 + 0.05 * np.sin(np.arange(n) / 30) + rng.normal(0, .02, n)
    # candidate wetter than the reference, with a drift so that the stability
    # slope of BIAS is clearly positive
    cand = ref + 0.04 + np.linspace(0, .03, n) + rng.normal(0, .02, n)
    # column order as the validation framework passes it: reference first
    return pd.DataFrame({"0-ISMN": ref, "1-C3S": cand}, index=idx)


def _calculators():
    return (PairwiseIntercomparisonMetrics(calc_kendall=False),
            CandidateMinusReferencePairwiseMetrics(calc_kendall=False))


def _assert_rest_identical(r_old, r_new, flipped_keys):
    assert set(r_old) == set(r_new)
    for k in r_old:
        if k in flipped_keys:
            continue
        a, b = np.asarray(r_old[k]), np.asarray(r_new[k])
        assert a.dtype == b.dtype, k
        if a.dtype.kind == "f":
            assert np.array_equal(a, b, equal_nan=True), k
        else:
            assert np.array_equal(a, b), k


def test_bias_is_candidate_minus_reference():
    df = _data()
    old, new = _calculators()
    r_old = old.calc_metrics(df, GPI)
    r_new = new.calc_metrics(df, GPI)

    expected = df["1-C3S"].mean() - df["0-ISMN"].mean()
    assert expected > 0
    # the result arrays are float32 in pytesmo's metric template
    np.testing.assert_allclose(r_new["BIAS"][0], expected, rtol=1e-6)
    assert r_new["BIAS"].dtype == r_old["BIAS"].dtype

    # exact negation of pytesmo's BIAS, confidence interval swapped
    assert r_new["BIAS"][0] == -r_old["BIAS"][0]
    assert r_new["BIAS_ci_lower"][0] == -r_old["BIAS_ci_upper"][0]
    assert r_new["BIAS_ci_upper"][0] == -r_old["BIAS_ci_lower"][0]
    assert r_new["BIAS_ci_lower"][0] < r_new["BIAS"][0] < r_new["BIAS_ci_upper"][0]


def test_other_metrics_bit_identical_to_pytesmo():
    df = _data()
    old, new = _calculators()
    _assert_rest_identical(old.calc_metrics(df, GPI),
                           new.calc_metrics(df, GPI), FLIPPED)
    # the result template is not modified
    assert np.isnan(new.result_template["BIAS"][0])


def test_insufficient_and_empty_data_stay_nan():
    _, new = _calculators()
    r = new.calc_metrics(_data(n=5), GPI)
    assert all(np.isnan(r[k][0]) for k in FLIPPED)

    # keyword call, as in spatial_validation_xr and temporal_validation_xr
    empty = pd.DataFrame([], columns=["0-ISMN", "1-C3S"])
    r = new.calc_metrics(data=empty, gpi_info=GPI)
    assert all(np.isnan(r[k][0]) for k in FLIPPED)


def test_intra_annual_subsets_follow_convention():
    df = _data()
    subsets = {
        "DJF": TsDistributor(yearless_date_ranges=[
            (YearlessDatetime(12, 1), YearlessDatetime(2, 28))]),
        "JJA": TsDistributor(yearless_date_ranges=[
            (YearlessDatetime(6, 1), YearlessDatetime(8, 31))]),
    }
    old, new = _calculators()
    r_old = SubsetsMetricsAdapter(old, subsets, "join").calc_metrics(df, GPI)
    r_new = SubsetsMetricsAdapter(new, subsets, "join").calc_metrics(df, GPI)

    for s in subsets:
        assert r_new[f"{s}|BIAS"][0] > 0
        assert r_new[f"{s}|BIAS"][0] == -r_old[f"{s}|BIAS"][0]
        assert r_new[f"{s}|BIAS_ci_lower"][0] == -r_old[f"{s}|BIAS_ci_upper"][0]
    _assert_rest_identical(
        r_old, r_new, {f"{s}|{m}" for s in subsets for m in FLIPPED})


def test_stability_slope_of_bias_follows_convention():
    df = _data()
    subsets = {
        str(y): TsDistributor(date_ranges=[
            (datetime(y, 1, 1), datetime(y, 12, 31, 23, 59))])
        for y in (2015, 2016, 2017)
    }
    subsets["bulk"] = TsDistributor(date_ranges=[
        (datetime(2015, 1, 1), datetime(2017, 12, 31, 23, 59))])
    old, new = _calculators()
    r_old = StabilityMetricsAdapter(old, subsets, "join").calc_metrics(df, GPI)
    r_new = StabilityMetricsAdapter(new, subsets, "join").calc_metrics(df, GPI)

    for s in subsets:
        assert r_new[f"{s}|BIAS"][0] == -r_old[f"{s}|BIAS"][0]
    # the candidate drifts wetter, so the slope of candidate - reference is > 0
    assert r_new["bulk|slopeBIAS"][0] > 0
    np.testing.assert_allclose(r_new["bulk|slopeBIAS"],
                               -r_old["bulk|slopeBIAS"], rtol=1e-12)
    for m in ("bulk|slopeR", "bulk|slopeURMSD"):
        assert np.array_equal(r_new[m], r_old[m], equal_nan=True), m


class TestBiasConventionMigration(TransactionTestCase):
    """
    Existing runs get False (old sign), new runs get True. This fails if
    0097 and 0098 are ever squashed into a single AddField(default=True).

    DELETE this test once production, staging and any dev databases restored
    from older dumps have applied 0097 and 0098. After that a squash can no
    longer mislabel old runs (databases that applied both skip it, fresh ones
    have no old runs), and the test only costs: it pins migration names, and
    its rollback to 0096 breaks as soon as a later validator migration is not
    reversible.
    """
    # like the other TransactionTestCases (e.g. TestValidationConfigView):
    # without it, the flush after this test re-creates the content types and a
    # later serialized_rollback test fails on loading them again
    serialized_rollback = True

    before = [('validator', '0096_datasetconfiguration_merge_weighted_and_more')]
    after = [('validator', '0098_alter_validationrun_bias_candidate_minus_reference')]

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_existing_runs_keep_old_convention(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.before)
        OldValidationRun = executor.loader.project_state(
            self.before).apps.get_model('validator', 'ValidationRun')
        old_run = OldValidationRun.objects.create(start_time=timezone.now())

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.after)
        NewValidationRun = executor.loader.project_state(
            self.after).apps.get_model('validator', 'ValidationRun')

        assert NewValidationRun.objects.get(
            pk=old_run.pk).bias_candidate_minus_reference is False
        new_run = NewValidationRun.objects.create(start_time=timezone.now())
        assert NewValidationRun.objects.get(
            pk=new_run.pk).bias_candidate_minus_reference is True
