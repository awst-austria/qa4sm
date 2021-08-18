import os

from django.contrib.auth import get_user_model

from validator.models import Dataset, DatasetVersion, DatasetConfiguration, ValidationRun, DataVariable, DataFilter, \
    ParametrisedFilter
from dateutil.tz import tzlocal
from datetime import datetime
from pytz import UTC
User = get_user_model()


def create_test_user():
    auth_data = {
        'username': 'chuck_norris',
        'password': 'roundhousekick'
    }

    user_data = {
        'username': auth_data['username'],
        'password': auth_data['password'],
        'email': 'norris@awst.at',
        'first_name': 'Chuck',
        'last_name': 'Norris',
        'organisation': 'Texas Rangers',
        'country': 'US',
        'orcid': '0000-0002-1825-0097',
    }
    User.objects.filter(email=user_data['email']).delete()
    test_user = User.objects.create_user(**user_data)
    test_user.save()
    print(test_user)
    return auth_data, test_user


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
    run.save()

    return run


def default_parameterized_validation(user, tcol=False):
    if not tcol:
        run = generate_default_validation()
    else:
        run = generate_default_validation_triple_coll()

    run.user = user
    run.scaling_method = ValidationRun.NO_SCALING

    run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
    run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)

    for config in run.dataset_configurations.all():
        if config == run.reference_configuration:
            config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
        else:
            config.filters.add(DataFilter.objects.get(name='FIL_C3S_FLAG_0'))
            config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

        config.save()

    pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='SCAN',
                                 dataset_config=run.reference_configuration)
    pfilter.save()
    pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0,0.1",
                                 dataset_config=run.reference_configuration)
    pfilter.save()

    return run


def delete_run(run):
    # delete output of test validations, clean up after ourselves
    ncfile = run.output_file.path
    outdir = os.path.dirname(ncfile)
    assert os.path.isfile(ncfile)
    run.delete()
    assert not os.path.exists(outdir)