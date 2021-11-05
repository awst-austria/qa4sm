from datetime import datetime
import logging
from os import path
from re import sub as regex_sub
import uuid

from celery.app import shared_task
from celery.exceptions import TaskRevokedError, TimeoutError
from dateutil.tz import tzlocal
from django.conf import settings
from django.urls.base import reverse

from netCDF4 import Dataset
from pytesmo.validation_framework.adapters import AnomalyAdapter, \
    AnomalyClimAdapter
from pytesmo.validation_framework.data_manager import DataManager
from pytesmo.validation_framework.metric_calculators import (
    get_dataset_names,
    PairwiseIntercomparisonMetrics,
    TripleCollocationMetrics,
)
from pytesmo.validation_framework.temporal_matchers import (
    make_combined_temporal_matcher,
)
import pandas as pd
from pytesmo.validation_framework.results_manager import netcdf_results_manager
from pytesmo.validation_framework.validation import Validation
from pytz import UTC
import pytz

from valentina.celery import app
from validator.mailer import send_val_done_notification
from validator.models import CeleryTask
from validator.models import ValidationRun, DatasetVersion
from validator.validation.batches import create_jobs, create_upscaling_lut
from validator.validation.filters import setup_filtering
from validator.validation.globals import OUTPUT_FOLDER, IRREGULAR_GRIDS
from validator.validation.graphics import generate_all_graphs
from validator.validation.readers import create_reader
from validator.validation.util import mkdir_if_not_exists, first_file_in
from validator.validation.globals import START_TIME, END_TIME, METADATA_TEMPLATE

__logger = logging.getLogger(__name__)


def _get_actual_time_range(val_run, dataset_version_id):
    try:
        vs_start = DatasetVersion.objects.get(pk=dataset_version_id).time_range_start
        vs_start_time = datetime.strptime(vs_start, '%Y-%m-%d').date()

        vs_end = DatasetVersion.objects.get(pk=dataset_version_id).time_range_end
        vs_end_time = datetime.strptime(vs_end, '%Y-%m-%d').date()

        val_start_time = val_run.interval_from.date()
        val_end_time = val_run.interval_to.date()

        actual_start = val_start_time.strftime('%Y-%m-%d') if val_start_time > vs_start_time \
            else vs_start_time.strftime('%Y-%m-%d')
        actual_end = val_end_time.strftime('%Y-%m-%d') if val_end_time < vs_end_time \
            else vs_end_time.strftime('%Y-%m-%d')

    except:
        # exception will arise for ISMN, and for that one we can use entire range
        actual_start = START_TIME
        actual_end = END_TIME

    return [actual_start, actual_end]


def _get_reference_reader(val_run):
    ref_reader = create_reader(val_run.reference_configuration.dataset, val_run.reference_configuration.version)

    # we do the dance with the filtering below because filter may actually change the original reader, see ismn network selection
    ref_reader = setup_filtering(
        ref_reader,
        list(val_run.reference_configuration.filters.all()),
        list(val_run.reference_configuration.parametrisedfilter_set.all()),
        val_run.reference_configuration.dataset,
        val_run.reference_configuration.variable
    )

    while hasattr(ref_reader, 'cls'):
        ref_reader = ref_reader.cls

    return ref_reader


def set_outfile(validation_run, run_dir):
    outfile = first_file_in(run_dir, '.nc')
    if outfile is not None:
        outfile = regex_sub('/?' + OUTPUT_FOLDER + '/?', '', outfile)
        validation_run.output_file.name = outfile


def save_validation_config(validation_run):
    try:
        ds = Dataset(path.join(OUTPUT_FOLDER, validation_run.output_file.name), "a", format="NETCDF4")

        ds.qa4sm_version = settings.APP_VERSION
        ds.qa4sm_env_url = settings.ENV_FILE_URL_TEMPLATE.format(settings.APP_VERSION)
        ds.url = settings.SITE_URL + reverse('result', kwargs={'result_uuid': validation_run.id})
        if validation_run.interval_from is None:
            ds.val_interval_from = "N/A"
        else:
            ds.val_interval_from = validation_run.interval_from.strftime('%Y-%m-%d %H:%M')

        if validation_run.interval_to is None:
            ds.val_interval_to = "N/A"
        else:
            ds.val_interval_to = validation_run.interval_to.strftime('%Y-%m-%d %H:%M')

        j = 1
        for dataset_config in validation_run.dataset_configurations.all():
            filters = None
            if dataset_config.filters.all():
                filters = '; '.join([x.description for x in dataset_config.filters.all()])
            if dataset_config.parametrisedfilter_set.all():
                if filters:
                    filters += ';'
                filters += '; '.join(
                    [pf.filter.description + " " + pf.parameters for pf in dataset_config.parametrisedfilter_set.all()])

            if not filters:
                filters = 'N/A'

            if (validation_run.reference_configuration and
                    (dataset_config.id == validation_run.reference_configuration.id)):
                i = 0  # reference is always 0
            else:
                i = j
                j += 1

            ds.setncattr('val_dc_dataset' + str(i), dataset_config.dataset.short_name)
            ds.setncattr('val_dc_version' + str(i), dataset_config.version.short_name)
            ds.setncattr('val_dc_variable' + str(i), dataset_config.variable.short_name)

            ds.setncattr('val_dc_dataset_pretty_name' + str(i), dataset_config.dataset.pretty_name)
            ds.setncattr('val_dc_version_pretty_name' + str(i), dataset_config.version.pretty_name)
            ds.setncattr('val_dc_variable_pretty_name' + str(i), dataset_config.variable.pretty_name)

            ds.setncattr('val_dc_filters' + str(i), filters)

            actual_interval_from, actual_interval_to = _get_actual_time_range(validation_run, dataset_config.version.id)
            ds.setncattr('val_dc_actual_interval_from' + str(i), actual_interval_from)
            ds.setncattr('val_dc_actual_interval_to' + str(i), actual_interval_to)

            if ((validation_run.reference_configuration is not None) and
                    (dataset_config.id == validation_run.reference_configuration.id)):
                ds.val_ref = 'val_dc_dataset' + str(i)

            if ((validation_run.scaling_ref is not None) and
                    (dataset_config.id == validation_run.scaling_ref.id)):
                ds.val_scaling_ref = 'val_dc_dataset' + str(i)
                if dataset_config.dataset.short_name in IRREGULAR_GRIDS.keys():
                    grid_stepsize = IRREGULAR_GRIDS[dataset_config.dataset.short_name]
                else:
                    grid_stepsize = 'nan'
                ds.setncattr('val_dc_dataset' + str(i) + '_grid_stepsize', grid_stepsize)

        ds.val_scaling_method = validation_run.scaling_method

        ds.val_anomalies = validation_run.anomalies
        if validation_run.anomalies == ValidationRun.CLIMATOLOGY:
            ds.val_anomalies_from = validation_run.anomalies_from.strftime('%Y-%m-%d %H:%M')
            ds.val_anomalies_to = validation_run.anomalies_to.strftime('%Y-%m-%d %H:%M')

        if all(x is not None for x in
               [validation_run.min_lat, validation_run.min_lon, validation_run.max_lat, validation_run.max_lon]):
            ds.val_spatial_subset = "[{}, {}, {}, {}]".format(validation_run.min_lat, validation_run.min_lon,
                                                              validation_run.max_lat, validation_run.max_lon)

        ds.close()
    except Exception:
        __logger.exception('Validation configuration could not be stored.')


def create_pytesmo_validation(validation_run):
    ds_list = []
    ref_name = None
    scaling_ref_name = None

    ds_num = 1
    for dataset_config in validation_run.dataset_configurations.all():
        reader = create_reader(dataset_config.dataset, dataset_config.version)
        reader = setup_filtering(reader, list(dataset_config.filters.all()),
                                 list(dataset_config.parametrisedfilter_set.all()),
                                 dataset_config.dataset, dataset_config.variable)

        if validation_run.anomalies == ValidationRun.MOVING_AVG_35_D:
            reader = AnomalyAdapter(reader, window_size=35, columns=[dataset_config.variable.pretty_name])
        if validation_run.anomalies == ValidationRun.CLIMATOLOGY:
            # make sure our baseline period is in UTC and without timezone information
            anomalies_baseline = [validation_run.anomalies_from.astimezone(tz=pytz.UTC).replace(tzinfo=None),
                                  validation_run.anomalies_to.astimezone(tz=pytz.UTC).replace(tzinfo=None)]
            reader = AnomalyClimAdapter(reader, columns=[dataset_config.variable.pretty_name],
                                        timespan=anomalies_baseline)

        if (validation_run.reference_configuration and
                (dataset_config.id == validation_run.reference_configuration.id)):
            # reference is always named "0-..."
            dataset_name = '{}-{}'.format(0, dataset_config.dataset.short_name)
        else:
            dataset_name = '{}-{}'.format(ds_num, dataset_config.dataset.short_name)
            ds_num += 1

        ds_list.append((dataset_name, {'class': reader, 'columns': [dataset_config.variable.pretty_name]}))

        if (validation_run.reference_configuration and
                (dataset_config.id == validation_run.reference_configuration.id)):
            ref_name = dataset_name
            ref_short_name = validation_run.reference_configuration.dataset.short_name

        if (validation_run.scaling_ref and
                (dataset_config.id == validation_run.scaling_ref.id)):
            scaling_ref_name = dataset_name

    datasets = dict(ds_list)
    ds_num = len(ds_list)

    period = None
    if validation_run.interval_from is not None and validation_run.interval_to is not None:
        # while pytesmo can't deal with timezones, normalise the validation period to utc; can be removed once pytesmo can do timezones
        startdate = validation_run.interval_from.astimezone(UTC).replace(tzinfo=None)
        enddate = validation_run.interval_to.astimezone(UTC).replace(tzinfo=None)
        period = [startdate, enddate]

    upscale_parms = None
    if validation_run.upscaling_method != "none":
        __logger.debug(
            "Upscaling option is active"
        )
        upscale_parms = {
            "upscaling_method": validation_run.upscaling_method,
            "temporal_stability": validation_run.temporal_stability,
        }
        upscaling_lut = create_upscaling_lut(
            validation_run=validation_run,
            datasets=datasets,
            ref_name=ref_name,
        )
        upscale_parms["upscaling_lut"] = upscaling_lut
        __logger.debug(
            "Lookup table for non-reference datasets " + ", ".join(upscaling_lut.keys()) + " created"
        )
        __logger.debug(
            "{}".format(upscaling_lut)
        )

    datamanager = DataManager(
        datasets,
        ref_name=ref_name,
        period=period,
        read_ts_names='read',
        upscale_parms=upscale_parms,
    )
    ds_names = get_dataset_names(datamanager.reference_name, datamanager.datasets, n=ds_num)

    # set value of the metadata template according to what reference dataset is used
    if ref_short_name == 'ISMN':
        metadata_template = METADATA_TEMPLATE['ismn_ref']
    else:
        metadata_template = METADATA_TEMPLATE['other_ref']

    pairwise_metrics = PairwiseIntercomparisonMetrics(
        metadata_template=metadata_template, calc_kendall=False,
    )

    metric_calculators = {(ds_num, 2): pairwise_metrics.calc_metrics}

    if (len(ds_names) >= 3) and (validation_run.tcol is True):
        tcol_metrics = TripleCollocationMetrics(
            ref_name,
            metadata_template=metadata_template,
            bootstrap_cis=validation_run.bootstrap_tcol_cis
        )
        metric_calculators.update({(ds_num, 3): tcol_metrics.calc_metrics})

    if validation_run.scaling_method == validation_run.NO_SCALING:
        scaling_method = None
    else:
        scaling_method = validation_run.scaling_method

    __logger.debug(f"Scaling method: {scaling_method}")
    __logger.debug(f"Scaling dataset: {scaling_ref_name}")

    val = Validation(
        datasets=datamanager,
        temporal_matcher=make_combined_temporal_matcher(pd.Timedelta(12, "H")),
        spatial_ref=ref_name,
        scaling=scaling_method,
        scaling_ref=scaling_ref_name,
        metrics_calculators=metric_calculators,
        period=period
    )

    return val


def num_gpis_from_job(job):
    try:
        num_gpis = len(job[0])
    except:
        num_gpis = 1

    return num_gpis


@shared_task(bind=True, max_retries=3)
def execute_job(self, validation_id, job):
    task_id = execute_job.request.id
    numgpis = num_gpis_from_job(job)
    __logger.debug("Executing job {} from validation {}, # of gpis: {}".format(task_id, validation_id, numgpis))
    start_time = datetime.now(tzlocal())
    try:
        validation_run = ValidationRun.objects.get(pk=validation_id)
        val = create_pytesmo_validation(validation_run)

        result = val.calc(*job, rename_cols=False, only_with_temporal_ref=True)
        end_time = datetime.now(tzlocal())
        duration = end_time - start_time
        duration = (duration.days * 86400) + duration.seconds
        __logger.debug(
            "Finished job {} from validation {}, took {} seconds for {} gpis".format(task_id, validation_id, duration,
                                                                                     numgpis))
        return result
    except Exception as e:
        self.retry(countdown=2, exc=e)


def check_and_store_results(job_id, results, save_path):
    if len(results) < 1:
        __logger.warning('Potentially problematic job: {} - no results'.format(job_id))
        return

    netcdf_results_manager(results, save_path)


def track_celery_task(validation_run, task_id):
    celery_task = CeleryTask()
    celery_task.validation = validation_run
    celery_task.celery_task_id = uuid.UUID(task_id).hex
    celery_task.save()


def celery_task_cancelled(task_id):
    # stop_running_validation deletes the validation's tasks from the db. so if they don't exist in the db the task was cancelled
    return not CeleryTask.objects.filter(celery_task_id=task_id).exists()


def untrack_celery_task(task_id):
    try:
        celery_task = CeleryTask.objects.get(celery_task_id=task_id)
        celery_task.delete()
    except CeleryTask.DoesNotExist:
        __logger.debug('Task {} already deleted from db.'.format(task_id))


def run_validation(validation_id):
    __logger.info("Starting validation: {}".format(validation_id))
    validation_run = ValidationRun.objects.get(pk=validation_id)
    validation_aborted = False;

    if (not hasattr(settings, 'CELERY_TASK_ALWAYS_EAGER')) or (not settings.CELERY_TASK_ALWAYS_EAGER):
        app.control.add_consumer(validation_run.user.username, reply=True)  # @UndefinedVariable

    try:
        run_dir = path.join(OUTPUT_FOLDER, str(validation_run.id))
        mkdir_if_not_exists(run_dir)

        ref_reader = _get_reference_reader(validation_run)

        total_points, jobs = create_jobs(
            validation_run=validation_run,
            reader=ref_reader,
            dataset_config=validation_run.reference_configuration
        )
        validation_run.total_points = total_points
        validation_run.save()  # save the number of gpis before we start

        __logger.debug("Jobs to run: {}".format([job[:-1] for job in jobs]))

        save_path = run_dir

        async_results = []
        job_table = {}
        for j in jobs:
            celery_job = execute_job.apply_async(args=[validation_id, j], queue=validation_run.user.username)
            async_results.append(celery_job)
            job_table[celery_job.id] = j
            track_celery_task(validation_run, celery_job.id)

        for async_result in async_results:
            try:
                if not validation_aborted:  # only wait for this task if the validation hasn't been cancelled
                    task_running = True
                    while task_running:  # regularly check if the validation has been cancelled in this loop, otherwise we wouldn't notice
                        try:
                            # this throws TimeoutError after waiting 10 secs or TaskRevokedError if revoked before starting
                            results = async_result.get(timeout=10)
                            # if we got here, the task is finished now; stop looping because task finished
                            task_running = False
                            # we can still have a cancelled validation that took less than 10 secs
                            if celery_task_cancelled(async_result.id):
                                validation_aborted = True
                            else:
                                untrack_celery_task(async_result.id)

                        except (TimeoutError, TaskRevokedError) as te:
                            # see if our task got cancelled - if not, just continue loop
                            if celery_task_cancelled(async_result.id):
                                task_running = False  # stop looping because we aborted
                                validation_aborted = True
                                __logger.debug(
                                    'Validation got cancelled, dropping task {}: {}'.format(async_result.id, te))

                # in case there where no points with overlapping data within
                # the validation period, results is an empty dictionary, and we
                # count this job as error
                if validation_aborted or not results:
                    validation_run.error_points += num_gpis_from_job(job_table[async_result.id])
                else:
                    results = _pytesmo_to_qa4sm_results(results)
                    check_and_store_results(async_result.id, results, run_dir)
                    validation_run.ok_points += num_gpis_from_job(job_table[async_result.id])

            except Exception as e:
                validation_run.error_points += num_gpis_from_job(job_table[async_result.id])
                __logger.exception(
                    'Celery could not execute the job. Job ID: {} Error: {}'.format(async_result.id, async_result.info))
                # forgetting task doesn't remove it, so cleaning has to be added here
                if celery_task_cancelled(async_result.id):
                    validation_aborted = True
                else:
                    untrack_celery_task(async_result.id)
            finally:
                # whether finished or cancelled or failed, forget about this task now
                async_result.forget()

            if not validation_aborted:
                validation_run.progress = round(
                    ((validation_run.ok_points + validation_run.error_points) / validation_run.total_points) * 100)
            else:
                validation_run.progress = -1
            validation_run.save()
            __logger.info("Dealt with task {}, validation {} is {} % done...".format(async_result.id, validation_run.id,
                                                                                     validation_run.progress))

        # once all tasks are finished:
        # only store parameters and produce graphs if validation wasn't cancelled and
        # we have metrics for at least one gpi - otherwise no netcdf output file
        if (not validation_aborted) and (validation_run.ok_points > 0):
            set_outfile(validation_run, run_dir)
            validation_run.save()
            save_validation_config(validation_run)
            generate_all_graphs(validation_run, run_dir)

    except Exception as e:
        __logger.exception('Unexpected exception during validation {}:'.format(validation_run))

    finally:
        validation_run.end_time = datetime.now(tzlocal())
        validation_run.save()
        __logger.info("Validation finished: {}. Jobs: {}, Errors: {}, OK: {}, End time: {} ".format(
            validation_run, validation_run.total_points, validation_run.error_points, validation_run.ok_points,
            validation_run.end_time))

        send_val_done_notification(validation_run)

    return validation_run


def stop_running_validation(validation_id):
    __logger.info("Stopping validation {} ".format(validation_id))
    validation_run = ValidationRun.objects.get(pk=validation_id)
    validation_run.progress = -1
    validation_run.save()

    celery_tasks = CeleryTask.objects.filter(validation=validation_run)

    for task in celery_tasks:
        app.control.revoke(task.celery_task_id)  # @UndefinedVariable
        task.delete()


def _pytesmo_to_qa4sm_results(results: dict) -> dict:
    """
    Converts the new pytesmo results dictionary format to the old format that
    is still used by QA4SM.

    Parameters
    ----------
    results : dict
        Each key in the dictionary is a tuple of ``((ds1, col1), (d2, col2))``,
        and the values contain the respective results for this combination of
        datasets/columns.

    Returns
    -------
    qa4sm_results : dict
        Dictionary in the format required by QA4SM. This involves merging the
        different dictionary entries from `results` to a single dictionary and
        renaming the metrics to avoid name clashes, using the naming convention
        from the old metric calculators.
    """
    # each key is a tuple of ((ds1, col1), (ds2, col2))
    # this adds all tuples to a single list, and then only
    # keeps unique entries
    qa4sm_key = tuple(sorted(set(sum(map(list, results.keys()), []))))

    qa4sm_res = {qa4sm_key: {}}
    for key in results:
        for metric in results[key]:
            # static 'metrics' (e.g. metadata, geoinfo) are not related to datasets
            statics = ["gpi", "n_obs", "lat", "lon"]
            statics.extend(METADATA_TEMPLATE["ismn_ref"])
            if metric in statics:
                new_key = metric
            else:
                datasets = list(map(lambda t: t[0], key))
                if isinstance(metric, tuple):
                    # happens only for triple collocation metrics, where the
                    # metric key is a tuple of (metric, dataset)
                    if metric[1].startswith("0-"):
                        # triple collocation metrics for the reference should
                        # not show up in the results
                        continue
                    new_metric = "_".join(metric)
                else:
                    new_metric = metric
                new_key = f"{new_metric}_between_{'_and_'.join(datasets)}"
            qa4sm_res[qa4sm_key][new_key] = results[key][metric]
    return qa4sm_res
