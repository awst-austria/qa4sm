# from dateutil.tz import tzlocal
# from datetime import datetime
# from validator.models import Dataset, DatasetVersion, DatasetConfiguration, ValidationRun, DataVariable
# from validator.validation.globals import ISMN_V20191211, ISMN, ISMN_soil_moisture, C3SC, C3S_sm, C3S_V202012, DEFAULT_TSW
# # ------------------------------------ Helper functions for generating validation runs ------------------------------------



# # Default reference/non-reference datasets
# default_reference_dataset = ISMN
# default_reference_version = ISMN_V20191211
# default_reference_variable = ISMN_soil_moisture

# default_non_reference_dataset = C3SC
# default_non_reference_version = C3S_V202012
# default_non_reference_variable = C3S_sm


# def create_dataset_configuration(run,
#                                  dataset,
#                                  version,
#                                  variable,
#                                  is_spatial_ref=False,
#                                  is_temporal_ref=False):
#     """ Helper function to create and save a DatasetConfiguration """
#     data_c = DatasetConfiguration()
#     data_c.validation = run
#     data_c.dataset = Dataset.objects.get(short_name=dataset)
#     data_c.version = DatasetVersion.objects.get(short_name=version)
#     data_c.variable = DataVariable.objects.get(pretty_name=variable)
#     data_c.is_spatial_reference = is_spatial_ref
#     data_c.is_temporal_reference = is_temporal_ref
#     data_c.save()
#     return data_c


# def set_intra_annual_metrics(run, metrics, metrics_type=None, overlap=0):
#     """ Helper function to set intra-annual metrics """
#     run.intra_annual_metrics = metrics
#     run.intra_annual_type = metrics_type
#     run.intra_annual_overlap = overlap
#     run.save()

# @print_defined_variables
# def generate_validation_run(dataset=default_non_reference_dataset,
#                             version=default_non_reference_version,
#                             variable=default_non_reference_variable,
#                             is_tcol=False,
#                             sbpca=False,
#                             reference_dataset=default_reference_dataset,
#                             reference_version=default_reference_version,
#                             reference_variable=default_reference_variable,
#                             intra_annual_metrics=False,
#                             intra_annual_type=None,
#                             intra_annual_overlap=0,
#                             extra_datasets=None):
#     """ Generalized function to generate a validation run """
#     run = ValidationRun()
#     run.start_time = datetime.now(tzlocal())
#     run.save()

#     # Create the primary dataset configuration
#     create_dataset_configuration(run, dataset, version, variable, False, False)

#     # Create reference dataset configuration
#     ref_c = create_dataset_configuration(run,
#                                          reference_dataset,
#                                          reference_version,
#                                          reference_variable,
#                                          is_spatial_ref=True,
#                                          is_temporal_ref=True)

#     # Set spatial_reference_configuration to ref_c explicitly
#     run.spatial_reference_configuration = ref_c
#     run.temporal_reference_configuration = ref_c
#     run.save()

#     # Handle triple collinearity or other extra datasets if applicable
#     if extra_datasets:
#         for extra in extra_datasets:
#             create_dataset_configuration(run, **extra)

#     # Set intra-annual metrics
#     set_intra_annual_metrics(run, intra_annual_metrics, intra_annual_type,
#                              intra_annual_overlap)

#     # Additional settings for triple coll
#     if is_tcol:
#         run.tcol = True
#         run.bootstrap_tcol_cis = True
#         run.save()
#     print(run.__dict__)
#     return run


# # ------------------------------------------ Specific validation run functions -----------------------------------------
# # here all the different validation runs are defined, with their specific settings
# # these are then used in valruns_for_tests.py to generate object holding the validation runs and expected results


# # Specific validation run functions (calling the generalized function)
# def generate_default_validation():
#     return generate_validation_run()


# def generate_default_validation_smos():
#     return generate_validation_run(dataset='SMOS_L3',
#                                    version='SMOSL3_v339_DESC',
#                                    variable='SMOSL3_sm')


# def generate_default_validation_smos_l2(sbpca=False):
#     dataset = 'SMOS_SBPCA' if sbpca else 'SMOS_L2'
#     version = 'SMOS_SBPCA_v724' if sbpca else 'SMOSL2_v700'
#     return generate_validation_run(dataset=dataset,
#                                    version=version,
#                                    variable='SMOSL2_sm')


# def generate_default_validation_triple_coll():
#     extra_datasets = [{
#         'dataset': 'SMOS_IC',
#         'version': 'SMOS_105_ASC',
#         'variable': 'SMOS_sm'
#     }]
#     return generate_validation_run(extra_datasets=extra_datasets, is_tcol=True)


# def generate_ismn_upscaling_validation():
#     """Generate a validation where ISMN is used as non-reference."""
#     return generate_validation_run(
#         # Swap the usual reference and non-reference datasets
#         dataset=default_reference_dataset,
#         version=default_reference_version,
#         variable=default_reference_variable,
#         reference_dataset=default_non_reference_dataset,
#         reference_version=default_non_reference_version,
#         reference_variable=default_non_reference_variable
#     )

# # Intra-annual metric variations


# def generate_default_seasonal_validation():
#     return generate_validation_run(intra_annual_metrics=True,
#                                    intra_annual_type='Seasonal')


# def generate_default_monthly_validation():
#     return generate_validation_run(intra_annual_metrics=True,
#                                    intra_annual_type='Monthly')


# def generate_default_seasonal_overlap_validation():
#     return generate_validation_run(intra_annual_metrics=True,
#                                    intra_annual_type='Seasonal',
#                                    intra_annual_overlap=20)
