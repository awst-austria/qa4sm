from validator.models import Dataset, DatasetVersion, DatasetConfiguration, ValidationRun, DataVariable
from dateutil.tz import tzlocal
from datetime import datetime
from validator.validation.globals import ISMN_V20191211, ISMN, ISMN_soil_moisture, C3SC, C3S_sm, C3S_V202012

default_reference_dataset = ISMN
default_reference_version = ISMN_V20191211
default_reference_variable = ISMN_soil_moisture

default_non_reference_dataset = C3SC
default_non_reference_version = C3S_V202012
default_non_reference_variable = C3S_sm

def generate_default_validation_hires():
    run = ValidationRun()
    run.plots_save_metadata = 'always'
    run.start_time = datetime.now(tzlocal())
    run.save()

    data_c = DatasetConfiguration()
    data_c.validation = run
    data_c.dataset = Dataset.objects.get(short_name='CGLS_CSAR_SSM1km')
    data_c.version = DatasetVersion.objects.get(short_name='CGLS_CSAR_SSM1km_V1_1')
    data_c.variable = DataVariable.objects.get(pretty_name='CGLS_SSM')
    data_c.is_spatial_reference = False
    data_c.is_temporal_reference = False
    data_c.save()

    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name=default_reference_dataset)
    ref_c.version = DatasetVersion.objects.get(short_name=default_reference_version)
    ref_c.variable = DataVariable.objects.get(pretty_name=default_reference_variable)
    ref_c.is_spatial_reference = True
    ref_c.is_temporal_reference = True
    ref_c.save()

    run.spatial_reference_configuration = ref_c
    run.temporal_reference_configuration = ref_c
    run.save()

    return run


def generate_default_validation():
    run = ValidationRun()
    run.start_time = datetime.now(tzlocal())
    run.save()

    data_c = DatasetConfiguration()
    data_c.validation = run
    data_c.dataset = Dataset.objects.get(short_name=default_non_reference_dataset)
    data_c.version = DatasetVersion.objects.get(short_name=default_non_reference_version)
    data_c.variable = DataVariable.objects.get(pretty_name=default_non_reference_variable)
    data_c.is_spatial_reference = False
    data_c.is_temporal_reference = False
    data_c.save()

    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name=default_reference_dataset)
    ref_c.version = DatasetVersion.objects.get(short_name=default_reference_version)
    ref_c.variable = DataVariable.objects.get(pretty_name=default_reference_variable)
    ref_c.is_spatial_reference = True
    ref_c.is_temporal_reference = True
    ref_c.save()

    run.spatial_reference_configuration = ref_c
    run.temporal_reference_configuration = ref_c
    run.save()

    return run


def generate_default_validation_smos():
    run = ValidationRun()
    run.start_time = datetime.now(tzlocal())
    run.save()

    data_c = DatasetConfiguration()
    data_c.validation = run
    data_c.dataset = Dataset.objects.get(short_name='SMOS_L3')
    data_c.version = DatasetVersion.objects.get(short_name='SMOSL3_v339_DESC')
    data_c.variable = DataVariable.objects.get(pretty_name='SMOSL3_sm')
    data_c.is_spatial_reference = False
    data_c.is_temporal_reference = False
    data_c.save()

    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name=default_reference_dataset)
    ref_c.version = DatasetVersion.objects.get(short_name=default_reference_version)
    ref_c.variable = DataVariable.objects.get(pretty_name=default_reference_variable)
    ref_c.is_spatial_reference = True
    ref_c.is_temporal_reference = True
    ref_c.save()

    run.spatial_reference_configuration = ref_c
    run.temporal_reference_configuration = ref_c
    run.save()

    return run


def generate_default_validation_smos_l2():
    run = ValidationRun()
    run.start_time = datetime.now(tzlocal())
    run.save()

    data_c = DatasetConfiguration()
    data_c.validation = run
    data_c.dataset = Dataset.objects.get(short_name='SMOS_L2')
    data_c.version = DatasetVersion.objects.get(short_name='SMOSL2_v700')
    data_c.variable = DataVariable.objects.get(pretty_name='SMOSL2_sm')
    data_c.is_spatial_reference = False
    data_c.is_temporal_reference = False
    data_c.save()

    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name=default_reference_dataset)
    ref_c.version = DatasetVersion.objects.get(short_name=default_reference_version)
    ref_c.variable = DataVariable.objects.get(pretty_name=default_reference_variable)
    ref_c.is_spatial_reference = True
    ref_c.is_temporal_reference = True
    ref_c.save()

    run.spatial_reference_configuration = ref_c
    run.temporal_reference_configuration = ref_c
    run.save()

    return run


def generate_default_validation_triple_coll():
    run = ValidationRun()
    run.start_time = datetime.now(tzlocal())
    run.save()

    data_c = DatasetConfiguration()
    data_c.validation = run
    data_c.dataset = Dataset.objects.get(short_name=default_non_reference_dataset)
    data_c.version = DatasetVersion.objects.get(short_name=default_non_reference_version)
    data_c.variable = DataVariable.objects.get(pretty_name=default_non_reference_variable)
    data_c.is_spatial_reference = False
    data_c.is_temporal_reference = False
    data_c.save()

    other_data_c = DatasetConfiguration()
    other_data_c.validation = run
    other_data_c.dataset = Dataset.objects.get(short_name='SMOS_IC')
    other_data_c.version = DatasetVersion.objects.get(short_name='SMOS_105_ASC')
    other_data_c.variable = DataVariable.objects.get(pretty_name='SMOS_sm')
    other_data_c.is_spatial_reference = False
    other_data_c.is_temporal_reference = False
    other_data_c.save()

    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name=default_reference_dataset)
    ref_c.version = DatasetVersion.objects.get(short_name=default_reference_version)
    ref_c.variable = DataVariable.objects.get(pretty_name=default_reference_variable)
    ref_c.is_spatial_reference = True
    ref_c.is_temporal_reference = True
    ref_c.save()

    run.spatial_reference_configuration = ref_c
    run.temporal_reference_configuration = ref_c
    run.tcol = True
    run.bootstrap_tcol_cis = True
    run.save()

    return run


def generate_ismn_upscaling_validation():
    """Generate a validation where ISMN is used as non-reference"""
    run = ValidationRun()
    run.start_time = datetime.now(tzlocal())
    run.save()

    # here ref and non ref switch places
    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name=default_non_reference_dataset)
    ref_c.version = DatasetVersion.objects.get(short_name=default_non_reference_version)
    ref_c.variable = DataVariable.objects.get(pretty_name=default_non_reference_variable)
    ref_c.is_spatial_reference = True
    ref_c.is_temporal_reference = True
    ref_c.save()

    data_c = DatasetConfiguration()
    data_c.validation = run
    data_c.dataset = Dataset.objects.get(short_name=default_reference_dataset)
    data_c.version = DatasetVersion.objects.get(short_name=default_reference_version)
    data_c.variable = DataVariable.objects.get(pretty_name=default_reference_variable)
    data_c.is_spatial_reference = False
    data_c.is_temporal_reference = False
    data_c.save()

    run.spatial_reference_configuration = ref_c
    run.temporal_reference_configuration = ref_c
    run.save()

    return run
