from os import path
from validator.tests.auxiliary_functions import (
    generate_ismn_upscaling_validation,
    generate_default_seasonal_validation,
    generate_default_monthly_validation,
    generate_default_seasonal_overlap_validation,
    generate_default_validation,
    generate_default_validation_triple_coll,
)
from validator.validation.globals import DEFAULT_TSW, TEMPORAL_SUB_WINDOWS
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, Optional, List
from enum import Enum


class TestValidationRunType(Enum):
    DEFAULT_BULK = "default_bulk"
    DEFAULT_SEASONAL = "default_seasonal"
    DEFAULT_MONTHLY = "default_monthly"
    DEFAULT_SEASONAL_OVERLAP = "default_seasonal_overlap"
    DEFAULT_TCOL_BULK = "default_tcol_bulk"
    BULK_ISMN_UPSCALING = "bulk_ismn_upscaling_validation"


@dataclass
class TestValidationRun:
    # Function to generate the validation run
    generate_val: Callable

    # further validation run attributes/results that we expect from the validation run generated above
    # test_validation_new.TestValidation.check_results() will check the test results against these defiend here
    # append new attributes here if needed
    intra_annual_metrics: bool
    intra_annual_type: Optional[str] = None
    intra_annual_overlap: int = 0
    temporal_sub_windows: List[str] = field(default_factory=list)
    test_validation_ccip_ref: Optional[Dict[str, int]] = None

    def results_tbe_dict(self):  # to be expected
        """Convert this object into a dictionary compatible with the current definiton of both \\
        `test_validation_new.TestValidation.check_results()` and \\
        `test_validation_new.TestValidation._check_validation_configuration_consistency()`
        """
        return {
            'intra_annual_metrics': self.intra_annual_metrics,
            'intra_annual_type': self.intra_annual_type,
            'intra_annual_overlap': self.intra_annual_overlap,
            'temporal_sub_windows': self.temporal_sub_windows,
            'test_validation_ccip_ref': self.test_validation_ccip_ref
        }


# -----------------------------LUTs holding validation runs alongside their expected results----------------------------

# Specific Validation Run Configurations
validations_runs_lut = {
    TestValidationRunType.DEFAULT_BULK:
    TestValidationRun(generate_val=generate_default_validation,
                      intra_annual_metrics=False,
                      temporal_sub_windows=[DEFAULT_TSW],
                      test_validation_ccip_ref={
                          'new_run_error_points': 8,
                          'new_run_ok_points': 16
                      }),
    TestValidationRunType.DEFAULT_SEASONAL:
    TestValidationRun(generate_val=generate_default_seasonal_validation,
                      intra_annual_metrics=True,
                      intra_annual_type='Seasonal',
                      temporal_sub_windows=[
                          DEFAULT_TSW,
                          *list(TEMPORAL_SUB_WINDOWS['seasons'].keys())
                      ],
                      test_validation_ccip_ref={
                          'new_run_error_points': 9,
                          'new_run_ok_points': 15
                      }),
    TestValidationRunType.DEFAULT_MONTHLY:
    TestValidationRun(generate_val=generate_default_monthly_validation,
                      intra_annual_metrics=True,
                      intra_annual_type='Monthly',
                      temporal_sub_windows=[
                          DEFAULT_TSW,
                          *list(TEMPORAL_SUB_WINDOWS['months'].keys())
                      ],
                      test_validation_ccip_ref={
                          'new_run_error_points': 9,
                          'new_run_ok_points': 15
                      }),
    TestValidationRunType.DEFAULT_SEASONAL_OVERLAP:
    TestValidationRun(
        generate_val=generate_default_seasonal_overlap_validation,
        intra_annual_metrics=True,
        intra_annual_type='Seasonal',
        intra_annual_overlap=20,
        temporal_sub_windows=[
            DEFAULT_TSW, *list(TEMPORAL_SUB_WINDOWS['seasons'].keys())
        ],
        test_validation_ccip_ref={
            'new_run_error_points': 9,
            'new_run_ok_points': 15
        }),
}

# Triple collocation validation runs
tcol_validations_runs_lut = {
    TestValidationRunType.DEFAULT_TCOL_BULK:
    TestValidationRun(generate_val=generate_default_validation_triple_coll,
                      intra_annual_metrics=False,
                      test_validation_ccip_ref={
                          'new_run_ok_points': 4,
                          'new_run_error_points': 5
                      }),
}

# ISMN upscaling validation runs
ismn_upscaling_validations_runs_lut = {
    TestValidationRunType.BULK_ISMN_UPSCALING:
    TestValidationRun(generate_val=generate_ismn_upscaling_validation,
                      intra_annual_metrics=False),
}
