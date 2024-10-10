from validator.models import Dataset
from os import path
from validator.tests.auxiliary_functions import (
    generate_ismn_upscaling_validation,
    generate_seasonal_ismn_upscaling_validation,
    generate_monthly_ismn_upscaling_validation,
    generate_seasonal_overlap_ismn_upscaling_validation,
    generate_default_seasonal_validation,
    generate_default_monthly_validation,
    generate_default_seasonal_overlap_validation,
    generate_default_seasonal_validation_triple_coll,
    generate_default_monthly_validation_triple_coll,
    generate_default_seasonal_overlap_validation_triple_coll,
    generate_default_validation,
    generate_default_validation_triple_coll,
)
from validator.validation.globals import DEFAULT_TSW, TEMPORAL_SUB_WINDOWS

def set_dataset_paths():
    for dataset in Dataset.objects.all():
        dataset.storage_path = path.join('testdata/input_data', dataset.short_name)
        dataset.save()

validations_runs_lut = {
            'default_bulk': [
                generate_default_validation, {
                    'intra_annual_metrics': False,
                    'intra_annual_type': None,
                    'intra_annual_overlap': 0,
                    'temporal_sub_wndws': [DEFAULT_TSW],
                    'test_validation_ccip_ref': {'new_run_error_points': 8,
                                                 'new_run_ok_points':  16}
                }
            ],
            'default_seasonal': [
                generate_default_seasonal_validation, {
                    'intra_annual_metrics': True,
                    'intra_annual_type': 'Seasonal',
                    'intra_annual_overlap': 0,
                    'temporal_sub_wndws': [*[DEFAULT_TSW], *[TEMPORAL_SUB_WINDOWS['seasons'].keys()]],
                    'test_validation_ccip_ref': {'new_run_error_points': 9,
                                                 'new_run_ok_points':  15}
                }
            ],
            'default_monthly': [
                generate_default_monthly_validation, {
                    'intra_annual_metrics': True,
                    'intra_annual_type': 'Monthly',
                    'intra_annual_overlap': 0,
                    'temporal_sub_wndws': [*[DEFAULT_TSW], *[TEMPORAL_SUB_WINDOWS['months'].keys()]],
                    'test_validation_ccip_ref': {'new_run_error_points': 9,
                                                 'new_run_ok_points':  15}
                }
            ],
            'default_seasonal_overlap': [
                generate_default_seasonal_overlap_validation, {
                    'intra_annual_metrics': True,
                    'intra_annual_type': 'Seasonal',
                    'intra_annual_overlap': 20,
                    'temporal_sub_wndws': [*[DEFAULT_TSW], *[TEMPORAL_SUB_WINDOWS['seasons'].keys()]],
                    'test_validation_ccip_ref': {'new_run_error_points': 9,
                                                 'new_run_ok_points':  15}
                }
            ],
        }


tcol_validations_runs_lut = {
            'default_tcol_bulk': [
                generate_default_validation_triple_coll, {
                    'intra_annual_metrics': False,
                    'intra_annual_type': None,
                    'intra_annual_overlap': 0,
                    'new_run_ok_points': 4,
                    'new_run_error_points': 5,
                }
            ],
            # presumably too little data for these to work

            # 'default_tcol_seasonal': [
            #     generate_default_seasonal_validation_triple_coll, {
            #         'intra_annual_metrics': True,
            #         'intra_annual_type': 'Seasonal',
            #         'intra_annual_overlap': 0,
            #         'new_run_ok_points': 0,
            #         'new_run_error_points': 0,
            #     }
            # ],
            # 'default_tcol_monthly': [
            #     generate_default_monthly_validation_triple_coll, {
            #         'intra_annual_metrics': True,
            #         'intra_annual_type': 'Monthly',
            #         'intra_annual_overlap': 0,
            #         'new_run_ok_points': 9,
            #         'new_run_error_points': 0,
            #     }
            # ],
            # 'default_tcol_seasonal_overlap': [
            #     generate_default_seasonal_overlap_validation_triple_coll, {
            #         'intra_annual_metrics': True,
            #         'intra_annual_type': 'Seasonal',
            #         'intra_annual_overlap': 20,
            #         'new_run_ok_points': 9,
            #         'new_run_error_points': 0,
            #     }
            # ],
        }

ismn_upscaling_validations_runs_lut = {
        'bulk_ismn_upscaling_validation': [
            generate_ismn_upscaling_validation, {
                'intra_annual_metrics': False,
                'intra_annual_type': None,
                'intra_annual_overlap': 0,
            }
        ],
        # 'seasonal_ismn_upscaling_validation': [
        #     generate_seasonal_ismn_upscaling_validation, {
        #         'intra_annual_metrics': True,
        #         'intra_annual_type': 'Seasonal',
        #         'intra_annual_overlap': 0,
        #     }
        # ],
        # 'monthly_ismn_upscaling_validation': [
        #     generate_monthly_ismn_upscaling_validation, {
        #         'intra_annual_metrics': True,
        #         'intra_annual_type': 'Monthly',
        #         'intra_annual_overlap': 0,
        #     }
        # ],
        # 'seasonal_overlap_ismn_upscaling_validation': [
        #     generate_seasonal_overlap_ismn_upscaling_validation, {
        #         'intra_annual_metrics': True,
        #         'intra_annual_type': 'Seasonal',
        #         'intra_annual_overlap': 20,
        #     }
        # ],
        }
