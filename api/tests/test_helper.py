import os

from django.contrib.auth import get_user_model

from validator.models import Dataset, DatasetVersion, DatasetConfiguration, ValidationRun, DataVariable, DataFilter, \
    ParametrisedFilter
from dateutil.tz import tzlocal
from datetime import datetime, timedelta
from pytz import UTC
from pytz import utc
from validator.validation import OUTPUT_FOLDER

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
    test_user.is_active = True
    test_user.save()
    return auth_data, test_user


def create_alternative_user():
    alternative_data = {
        'username': 'cheating_cheater',
        'password': 'cheatingalldaylong'
    }

    alternative_user_data = {
        'username': alternative_data['username'],
        'password': alternative_data['password'],
        'email': 'cheater@awst.at',
        'first_name': 'Chuck',
        'last_name': 'Norris',
        'organisation': 'Texas Rangers',
        'country': 'US',
        'orcid': '0000-0002-1825-0097',
    }

    User.objects.filter(email=alternative_user_data['email']).delete()
    test_user = User.objects.create_user(**alternative_user_data)
    test_user.save()
    return alternative_user_data, test_user


def generate_default_validation():
    run = ValidationRun()
    run.start_time = datetime.now(tzlocal())
    run.save()

    data_c = DatasetConfiguration()
    data_c.validation = run
    data_c.dataset = Dataset.objects.get(short_name='C3S_combined')
    data_c.version = DatasetVersion.objects.get(short_name='C3S_V202012')
    data_c.variable = DataVariable.objects.get(pretty_name='C3S_sm')
    data_c.is_scaling_reference = False
    data_c.is_spatial_reference = False
    data_c.is_temporal_reference = False
    data_c.save()

    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name='ISMN')
    ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
    ref_c.variable = DataVariable.objects.get(pretty_name='ISMN_soil_moisture')
    ref_c.is_spatial_reference = True
    ref_c.is_temporal_reference = True
    ref_c.is_scaling_reference = False
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
    data_c.dataset = Dataset.objects.get(short_name='C3S_combined')
    data_c.version = DatasetVersion.objects.get(short_name='C3S_V201912')
    data_c.variable = DataVariable.objects.get(pretty_name='C3S_sm')
    data_c.is_scaling_reference = False
    data_c.is_spatial_reference = False
    data_c.is_temporal_reference = False
    data_c.save()

    other_data_c = DatasetConfiguration()
    other_data_c.validation = run
    other_data_c.dataset = Dataset.objects.get(short_name='SMOS_IC')
    other_data_c.version = DatasetVersion.objects.get(short_name='SMOS_105_ASC')
    other_data_c.variable = DataVariable.objects.get(pretty_name='SMOS_sm')
    other_data_c.is_scaling_reference = False
    other_data_c.is_spatial_reference = False
    other_data_c.is_temporal_reference = False
    other_data_c.save()

    ref_c = DatasetConfiguration()
    ref_c.validation = run
    ref_c.dataset = Dataset.objects.get(short_name='ISMN')
    ref_c.version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
    ref_c.variable = DataVariable.objects.get(pretty_name='ISMN_soil_moisture')
    ref_c.is_spatial_reference = True
    ref_c.is_temporal_reference = True
    ref_c.is_scaling_reference = False
    ref_c.save()

    run.spatial_reference_configuration = ref_c
    run.tcol = True
    run.save()

    return run


def default_parameterized_validation_to_be_run(user, tcol=False):
    if not tcol:
        run = generate_default_validation()
    else:
        run = generate_default_validation_triple_coll()

    run.user = user
    run.scaling_method = ValidationRun.NO_SCALING

    run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
    run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)

    for config in run.dataset_configurations.all():
        if config == run.spatial_reference_configuration:
            config.filters.add(DataFilter.objects.get(name='FIL_ISMN_GOOD'))
        else:
            config.filters.add(DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

        config.save()

    pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='SCAN',
                                 dataset_config=run.spatial_reference_configuration)
    pfilter.save()
    pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0,0.1",
                                 dataset_config=run.spatial_reference_configuration)
    pfilter.save()

    return run


def create_default_validation_without_running(user, tcol=False):
    run = default_parameterized_validation_to_be_run(user, tcol)
    run.start_time = datetime.now(UTC) - timedelta(hours=1)
    run.end_time = datetime.now(UTC)
    run.total_points = 30
    run.error_points = 5
    run.anomalies = 'climatology'
    run.anomalies_from = datetime(1990, 1, 1, 0, 0, tzinfo=UTC)
    run.anomalies_to = datetime(2010, 12, 31, 23, 59, 59, tzinfo=UTC)
    run.output_file.name = str(run.id) + '/foobar.nc'
    run.save()

    return run


def delete_run(run):
    # delete output of test validations, clean up after ourselves
    try:
        ncfile = run.output_file.path
        outdir = os.path.dirname(ncfile)
        assert os.path.isfile(ncfile)
    except ValueError:
        # if there is no file assign to the validation it will no remove the empty
        outdir = os.path.join(OUTPUT_FOLDER, str(run.id))
    run.delete()
    assert not os.path.exists(outdir)