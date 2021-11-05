from validator.models import Dataset, DatasetVersion, DatasetConfiguration, ValidationRun, DataVariable
from dateutil.tz import tzlocal
from datetime import datetime


def generate_default_validation():
    run = ValidationRun()
    run.start_time = datetime.now(tzlocal())
    run.save()

    data_c = DatasetConfiguration()
    data_c.validation = run
    data_c.dataset = Dataset.objects.get(short_name='C3S')
    data_c.version = DatasetVersion.objects.get(short_name='C3S_V202012')
    data_c.variable = DataVariable.objects.get(short_name='C3S_sm')
    data_c.save()

    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name='ISMN')
    ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
    ref_c.variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')
    ref_c.save()

    run.reference_configuration = ref_c
    run.scaling_ref = ref_c
    run.save()

    return run


def generate_default_validation_triple_coll():
    run = ValidationRun()
    run.start_time = datetime.now(tzlocal())
    run.save()

    data_c = DatasetConfiguration()
    data_c.validation = run
    data_c.dataset = Dataset.objects.get(short_name='C3S')
    data_c.version = DatasetVersion.objects.get(short_name='C3S_V201912')
    data_c.variable = DataVariable.objects.get(short_name='C3S_sm')
    data_c.save()

    other_data_c = DatasetConfiguration()
    other_data_c.validation = run
    other_data_c.dataset = Dataset.objects.get(short_name='SMOS')
    other_data_c.version = DatasetVersion.objects.get(short_name='SMOS_105_ASC')
    other_data_c.variable = DataVariable.objects.get(short_name='SMOS_sm')
    other_data_c.save()

    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name='ISMN')
    ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
    ref_c.variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')
    ref_c.save()

    run.reference_configuration = ref_c
    run.scaling_ref = ref_c
    run.tcol = True
    run.bootstrap_tcol_cis = True
    run.save()

    return run


def generate_ismn_nonref_validation():
    """Generate a validation where ISMN is used as non-reference"""
    run = ValidationRun()
    run.start_time = datetime.now(tzlocal())
    run.save()

    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name='C3S')
    ref_c.version = DatasetVersion.objects.get(short_name='C3S_V202012')
    ref_c.variable = DataVariable.objects.get(short_name='C3S_sm')
    ref_c.save()

    data_c = DatasetConfiguration()
    data_c.validation = run
    data_c.dataset = Dataset.objects.get(short_name='ISMN')
    data_c.version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
    data_c.variable = DataVariable.objects.get(short_name='ISMN_soil_moisture')
    data_c.save()

    run.reference_configuration = ref_c
    run.scaling_ref = ref_c
    run.save()

    return run
