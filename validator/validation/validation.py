import netCDF4
from datetime import datetime
import logging
import os
from re import sub as regex_sub
import uuid
import ast
from shutil import copy2, copytree
from typing import List, Tuple, Dict, Union

from celery.app import shared_task
from celery.exceptions import TaskRevokedError, TimeoutError
from dateutil.tz import tzlocal
from django.conf import settings

from pytesmo.validation_framework.adapters import AnomalyAdapter, AnomalyClimAdapter
from pytesmo.validation_framework.data_manager import DataManager
from pytesmo.validation_framework.metric_calculators import (
    get_dataset_names,
    PairwiseIntercomparisonMetrics,
    TripleCollocationMetrics,
)
from pytesmo.validation_framework.temporal_matchers import (
    make_combined_temporal_matcher, )
import pandas as pd
from pytesmo.validation_framework.results_manager import netcdf_results_manager, build_filename
from pytesmo.validation_framework.validation import Validation
from pytesmo.validation_framework.metric_calculators_adapters import SubsetsMetricsAdapter, TsDistributor

from pytz import UTC
import pytz

from valentina.celery import app

from api.frontend_urls import get_angular_url

from validator.mailer import send_val_done_notification
from validator.models import CeleryTask, DatasetConfiguration, CopiedValidations
from validator.models import ValidationRun, DatasetVersion
from validator.validation.batches import create_jobs, create_upscaling_lut
from validator.validation.filters import setup_filtering
from validator.validation.globals import OUTPUT_FOLDER, IRREGULAR_GRIDS, VR_FIELDS, DS_FIELDS, ISMN, DEFAULT_TSW, TEMPORAL_SUB_WINDOW_SEPARATOR, METRICS
from validator.validation.graphics import generate_all_graphs
from validator.validation.readers import create_reader, adapt_timestamp
from validator.validation.util import mkdir_if_not_exists, first_file_in
from validator.validation.globals import START_TIME, END_TIME, METADATA_TEMPLATE

import qa4sm_reader
from qa4sm_reader.intra_annual_temp_windows import TemporalSubWindowsCreator, NewSubWindow
from qa4sm_reader.netcdf_transcription import Pytesmo2Qa4smResultsTranscriber

__logger = logging.getLogger(__name__)

def _get_actual_time_range(val_run, dataset_version_id):
    try:
        vs_start = DatasetVersion.objects.get(
            pk=dataset_version_id).time_range_start
        vs_start_time = datetime.strptime(vs_start, '%Y-%m-%d').date()

        vs_end = DatasetVersion.objects.get(
            pk=dataset_version_id).time_range_end
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


def _get_spatial_reference_reader(val_run) -> Tuple['Reader', str, dict]:
    ref_reader = create_reader(val_run.spatial_reference_configuration.dataset,
                               val_run.spatial_reference_configuration.version)

    time_adapted_ref_reader = adapt_timestamp(
        ref_reader, val_run.spatial_reference_configuration.dataset,
        val_run.spatial_reference_configuration.version)

    # we do the dance with the filtering below because filter may actually change the original reader, see ismn network selection
    filtered_reader, read_name, read_kwargs = \
        setup_filtering(
            reader=time_adapted_ref_reader,
            filters=list(val_run.spatial_reference_configuration.filters.all()),
            param_filters=list(val_run.spatial_reference_configuration.parametrisedfilter_set.all()),
            dataset=val_run.spatial_reference_configuration.dataset,
            variable=val_run.spatial_reference_configuration.variable)

    while hasattr(ref_reader, 'cls'):
        ref_reader = ref_reader.cls

    return ref_reader, read_name, read_kwargs


def set_outfile(validation_run, run_dir):
    outfile = first_file_in(run_dir, '.nc')
    if outfile is not None:
        outfile = regex_sub('/?' + OUTPUT_FOLDER + '/?', '', outfile)
        validation_run.output_file.name = outfile


def save_validation_config(validation_run):
    try:
        with netCDF4.Dataset(os.path.join(OUTPUT_FOLDER, validation_run.output_file.name),
                     "a",
                     format="NETCDF4") as ds:

            ds.qa4sm_version = settings.APP_VERSION
            ds.qa4sm_reader_version = qa4sm_reader.__version__
            ds.qa4sm_env_url = settings.ENV_FILE_URL_TEMPLATE.format(
                settings.APP_VERSION)
            ds.url = settings.SITE_URL + get_angular_url(
                'result', validation_run.id)
            if validation_run.interval_from is None:
                ds.val_interval_from = "N/A"
            else:
                ds.val_interval_from = validation_run.interval_from.strftime(
                    '%Y-%m-%d %H:%M')

            if validation_run.interval_to is None:
                ds.val_interval_to = "N/A"
            else:
                ds.val_interval_to = validation_run.interval_to.strftime(
                    '%Y-%m-%d %H:%M')

            j = 1
            for dataset_config in validation_run.dataset_configurations.all():
                filters = None
                if dataset_config.filters.all():
                    filters = '; '.join(
                        [x.description for x in dataset_config.filters.all()])
                if dataset_config.parametrisedfilter_set.all():
                    if filters:
                        filters += ';'
                    _list_comp = [
                        pf.filter.description + " " + pf.parameters
                        for pf in dataset_config.parametrisedfilter_set.all()
                        ]
                    try:
                        filters += '; '.join(_list_comp)
                    except TypeError as e:
                        __logger.error(f"Error in save_validation_config: {e}. {filters=}{_list_comp=}")
                        filters = '; '.join(_list_comp)

                if not filters:
                    filters = 'N/A'

                if (validation_run.spatial_reference_configuration and
                    (dataset_config.id
                     == validation_run.spatial_reference_configuration.id)):
                    i = 0  # reference is always 0
                else:
                    i = j
                    j += 1

                # there is no error for variables!!, there were some inconsistency with short and pretty names,
                # and it should be like that now
                ds.setncattr('val_dc_dataset' + str(i),
                             dataset_config.dataset.short_name)
                ds.setncattr('val_dc_version' + str(i),
                             dataset_config.version.short_name)
                ds.setncattr('val_dc_variable' + str(i),
                             dataset_config.variable.pretty_name)
                ds.setncattr('val_dc_unit' + str(i),
                             dataset_config.variable.unit)

                ds.setncattr('val_dc_dataset_pretty_name' + str(i),
                             dataset_config.dataset.pretty_name)
                ds.setncattr('val_dc_version_pretty_name' + str(i),
                             dataset_config.version.pretty_name)
                ds.setncattr('val_dc_variable_pretty_name' + str(i),
                             dataset_config.variable.short_name)

                ds.setncattr('val_dc_filters' + str(i), filters)

                actual_interval_from, actual_interval_to = _get_actual_time_range(
                    validation_run, dataset_config.version.id)
                ds.setncattr('val_dc_actual_interval_from' + str(i),
                             actual_interval_from)
                ds.setncattr('val_dc_actual_interval_to' + str(i),
                             actual_interval_to)

                if ((validation_run.spatial_reference_configuration
                     is not None) and
                    (dataset_config.id
                     == validation_run.spatial_reference_configuration.id)):
                    ds.val_ref = 'val_dc_dataset' + str(i)

                    try:
                        ds.setncattr(
                            'val_resolution',
                            validation_run.spatial_reference_configuration.
                            dataset.resolution["value"])
                        ds.setncattr(
                            'val_resolution_unit',
                            validation_run.spatial_reference_configuration.
                            dataset.resolution["unit"])
                    # ISMN has null resolution attribute, therefore
                    # we write no output resolution
                    except (AttributeError, TypeError):
                        pass

                if ((validation_run.scaling_ref is not None) and
                    (dataset_config.id == validation_run.scaling_ref.id)):
                    ds.val_scaling_ref = 'val_dc_dataset' + str(i)

                if dataset_config.dataset.short_name in IRREGULAR_GRIDS.keys():
                    grid_stepsize = IRREGULAR_GRIDS[
                        dataset_config.dataset.short_name]
                else:
                    grid_stepsize = 'nan'
                ds.setncattr('val_dc_dataset' + str(i) + '_grid_stepsize',
                             grid_stepsize)

            ds.val_scaling_method = validation_run.scaling_method

            ds.val_anomalies = validation_run.anomalies
            if validation_run.anomalies == ValidationRun.CLIMATOLOGY:
                ds.val_anomalies_from = validation_run.anomalies_from.strftime(
                    '%Y-%m-%d %H:%M')
                ds.val_anomalies_to = validation_run.anomalies_to.strftime(
                    '%Y-%m-%d %H:%M')

            if all(x is not None for x in [
                    validation_run.min_lat, validation_run.min_lon,
                    validation_run.max_lat, validation_run.max_lon
            ]):
                ds.val_spatial_subset = "[{}, {}, {}, {}]".format(
                    validation_run.min_lat, validation_run.min_lon,
                    validation_run.max_lat, validation_run.max_lon)

    except Exception:
        __logger.exception('Validation configuration could not be stored.')

def create_pytesmo_validation(validation_run):
    ds_list = []
    ds_read_names = []
    spatial_ref_name = None
    scaling_ref_name = None
    temporal_ref_name = None
    spatial_ref_short_name = None

    ds_num = 1
    for dataset_config in validation_run.dataset_configurations.all():
        reader = create_reader(dataset_config.dataset, dataset_config.version)

        time_adapted_reader = adapt_timestamp(reader, dataset_config.dataset,
                                              dataset_config.version)

        reader, read_name, read_kwargs = \
            setup_filtering(
                reader=time_adapted_reader,
                filters=list(dataset_config.filters.all()),
                param_filters=list(dataset_config.parametrisedfilter_set.all()),
                dataset=dataset_config.dataset,
                variable=dataset_config.variable)

        if validation_run.anomalies == ValidationRun.MOVING_AVG_35_D:
            reader = AnomalyAdapter(
                reader,
                window_size=35,
                columns=[dataset_config.variable.short_name],
                read_name=read_name)
        if validation_run.anomalies == ValidationRun.CLIMATOLOGY:
            # make sure our baseline period is in UTC and without timezone information
            anomalies_baseline = [
                validation_run.anomalies_from.astimezone(tz=pytz.UTC).replace(
                    tzinfo=None),
                validation_run.anomalies_to.astimezone(tz=pytz.UTC).replace(
                    tzinfo=None)
            ]
            reader = AnomalyClimAdapter(
                reader,
                columns=[dataset_config.variable.short_name],
                timespan=anomalies_baseline,
                read_name=read_name)

        if (validation_run.spatial_reference_configuration
                and (dataset_config.id
                     == validation_run.spatial_reference_configuration.id)):
            # reference is always named "0-..."
            dataset_name = '{}-{}'.format(0, dataset_config.dataset.short_name)
        else:
            dataset_name = '{}-{}'.format(ds_num,
                                          dataset_config.dataset.short_name)
            ds_num += 1

        ds_list.append((dataset_name, {
            'class': reader,
            'columns': [dataset_config.variable.short_name],
            'kwargs': read_kwargs,
            'max_dist': dataset_config.dataset.resolution_in_m
        }))
        ds_read_names.append((dataset_name, read_name))

        if (validation_run.spatial_reference_configuration
                and (dataset_config.id
                     == validation_run.spatial_reference_configuration.id)):
            spatial_ref_name = dataset_name
            spatial_ref_short_name = validation_run.spatial_reference_configuration.dataset.short_name

        if (validation_run.scaling_ref
                and (dataset_config.id == validation_run.scaling_ref.id)):
            scaling_ref_name = dataset_name

        if (validation_run.temporal_reference_configuration
                and (dataset_config.id
                     == validation_run.temporal_reference_configuration.id)):
            temporal_ref_name = dataset_name

    datasets = dict(ds_list)
    ds_num = len(ds_list)

    period = get_period(validation_run)

    __logger.debug(f"First: Validation period: {period}")
    upscale_parms = None
    if validation_run.upscaling_method != "none":
        __logger.debug("Upscaling option is active")
        upscale_parms = {
            "upscaling_method": validation_run.upscaling_method,
            "temporal_stability": validation_run.temporal_stability,
        }
        upscaling_lut = create_upscaling_lut(
            validation_run=validation_run,
            datasets=datasets,
            spatial_ref_name=spatial_ref_name,
        )
        upscale_parms["upscaling_lut"] = upscaling_lut
        __logger.debug("Lookup table for non-reference datasets " +
                       ", ".join(upscaling_lut.keys()) + " created")
        __logger.debug("{}".format(upscaling_lut))

    datamanager = DataManager(
        datasets,
        ref_name=spatial_ref_name,
        period=period,
        read_ts_names=dict(ds_read_names),
        upscale_parms=upscale_parms,
    )
    ds_names = get_dataset_names(datamanager.reference_name,
                                 datamanager.datasets,
                                 n=ds_num)

    # set value of the metadata template according to what reference dataset is used
    if spatial_ref_short_name == ISMN:
        metadata_template = METADATA_TEMPLATE['ismn_ref']
    else:
        metadata_template = METADATA_TEMPLATE['other_ref']

    _pairwise_metrics = PairwiseIntercomparisonMetrics(
        metadata_template=metadata_template,
        calc_kendall=False,
    )

    # as all testfiles and tests in the qa4sm_reader package still have Kendall's tau included and
    # qa4sm get's its list of METRICS from the qa4sm_reader.globals.py. In the line above "calc_kendall=False", which
    # means that in the qa4sm_reader.globals.py the METRICS needs to be manually set to exclude Kendall's tau.
    # to streamline the process, smth like this could be done:

    # if all(metric in METRICS for metric in ['tau', 'p_tau']):
    #   _calc_kendall = True
    # else:
    #  _calc_kendall = False

    # _pairwise_metrics = PairwiseIntercomparisonMetrics(
    #     metadata_template=metadata_template,
    #     calc_kendall=_calc_kendall,
    # )



    # intra-annual metrics
    iam_dict = define_intra_annual_metrics(validation_run)
    temp_sub_wdw_instance = iam_dict['temp_sub_wdw_instance']
    temp_sub_wdws = iam_dict['temp_sub_wdws']

    if isinstance(
            temp_sub_wdws, dict
    ):  # for more info, doc at see https://pytesmo.readthedocs.io/en/latest/examples/validation_framework.html#Metric-Calculator-Adapters
        pairwise_metrics = SubsetsMetricsAdapter(
            calculator=_pairwise_metrics,
            subsets=temp_sub_wdw_instance.custom_temporal_sub_windows,
            group_results="join",
        )

    elif temp_sub_wdws is None: # the default case
        pairwise_metrics = _pairwise_metrics

    else:
        raise ValueError(
            f"Invalid value for temp_sub_wdws: {temp_sub_wdws}. Please specify either None or a custom temporal sub windowing function."
        )

    metric_calculators = {(ds_num, 2): pairwise_metrics.calc_metrics}

    if (len(ds_names) >= 3) and (validation_run.tcol is True):
        _tcol_metrics = TripleCollocationMetrics(
            spatial_ref_name,
            metadata_template=metadata_template,
            bootstrap_cis=validation_run.bootstrap_tcol_cis)

        if isinstance(
                temp_sub_wdws, dict
        ):
            tcol_metrics = SubsetsMetricsAdapter(
                calculator=_tcol_metrics,
                subsets=temp_sub_wdw_instance.custom_temporal_sub_windows,
                group_results="join",
            )

        elif temp_sub_wdws is None:
            tcol_metrics = _tcol_metrics

        metric_calculators.update({(ds_num, 3): tcol_metrics.calc_metrics})


    if validation_run.scaling_method == validation_run.NO_SCALING:
        scaling_method = None
    else:
        scaling_method = validation_run.scaling_method

    __logger.debug(f"Scaling method: {scaling_method}")
    __logger.debug(f"Scaling dataset: {scaling_ref_name}")
    __logger.debug(f"Validation period: {period}")

    temporalwindow_size = validation_run.temporal_matching
    __logger.debug(
        f"Size of the temporal matching window: {temporalwindow_size} "
        f"{'hour' if temporalwindow_size == 1 else 'hours'}")

    val = Validation(
        datasets=datamanager,
        temporal_matcher=
        make_combined_temporal_matcher(  #? do i have to update that for intra-annual metrics?
            pd.Timedelta(temporalwindow_size / 2, "H")),
        temporal_ref=temporal_ref_name,
        spatial_ref=spatial_ref_name,
        scaling=scaling_method,
        scaling_ref=scaling_ref_name,
        metrics_calculators=metric_calculators,
        period=period)

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
    __logger.debug("Executing job {} from validation {}, # of gpis: {}".format(
        task_id, validation_id, numgpis))
    start_time = datetime.now(tzlocal())
    try:
        validation_run = ValidationRun.objects.get(pk=validation_id)
        val = create_pytesmo_validation(validation_run)

        result = val.calc(*job,
                          rename_cols=False,
                          only_with_reference=True,
                          handle_errors="ignore")
        end_time = datetime.now(tzlocal())
        duration = end_time - start_time
        duration = (duration.days * 86400) + duration.seconds
        __logger.debug(
            "Finished job {} from validation {}, took {} seconds for {} gpis".
            format(task_id, validation_id, duration, numgpis))
        return result
    except Exception as e:
        self.retry(countdown=2, exc=e)


def check_and_store_results(job_id, results, save_path):
    if len(results) < 1:
        __logger.warning(
            'Potentially problematic job: {} - no results'.format(job_id))
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
    validation_aborted = False

    if (not hasattr(settings, 'CELERY_TASK_ALWAYS_EAGER')) or (
            not settings.CELERY_TASK_ALWAYS_EAGER):
        app.control.add_consumer(validation_run.user.username,
                                 reply=True)  # @UndefinedVariable

    try:
        run_dir = os.path.join(OUTPUT_FOLDER, str(validation_run.id))
        mkdir_if_not_exists(run_dir)

        ref_reader, read_name, read_kwargs = _get_spatial_reference_reader(
            validation_run)

        total_points, jobs = create_jobs(
            validation_run=validation_run,
            reader=ref_reader,
            dataset_config=validation_run.spatial_reference_configuration)

        validation_run.total_points = total_points
        validation_run.save()  # save the number of gpis before we start

        __logger.debug("Jobs to run: {}".format([job[:-1] for job in jobs]))

        save_path = run_dir

        async_results = []
        job_table = {}
        for j in jobs:
            celery_job = execute_job.apply_async(
                args=[validation_id, j], queue=validation_run.user.username)
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
                                    'Validation got cancelled, dropping task {}: {}'
                                    .format(async_result.id, te))

                # in case there where no points with overlapping data within
                # the validation period, results is an empty dictionary, and we
                # count this job as error
                if validation_aborted or not results:
                    validation_run.error_points += num_gpis_from_job(
                        job_table[async_result.id])
                else:
                    results = _pytesmo_to_qa4sm_results(results)
                    check_and_store_results(async_result.id, results, run_dir)

                    # If the job ran successfully, we have to check the status
                    # attribute to see if the job actually calculated something
                    # (ok) or had an error.
                    # In principle we might have different result status for
                    # different dataset combinations, because it might happen
                    # that in one case the validation fails because there is
                    # not enough data. For "ok_points" we only count the points
                    # where all validations fail.

                    result_key = list(results.keys())[0]  # there is only 1 key
                    res = results[result_key]
                    status_result_keys = list(
                        filter(lambda s: "status" in s, res.keys()))
                    ok = res[status_result_keys[0]] == 0
                    for statkey in status_result_keys[1:]:
                        ok = ok & (res[statkey] == 0)
                    ngpis = num_gpis_from_job(
                        job_table[async_result.id]
                    )  #? so we need a new criterion to determine, if the job was ok or not? like ngpis * len(time slices)
                    nok = sum(ok)
                    validation_run.ok_points += nok
                    validation_run.error_points += ngpis - nok

            except Exception as e:
                validation_run.error_points += num_gpis_from_job(
                    job_table[async_result.id])
                __logger.exception(
                    'Celery could not execute the job. Job ID: {} Error: {}'.
                    format(async_result.id, async_result.info))
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
                    ((validation_run.ok_points + validation_run.error_points) /
                     validation_run.total_points) * 100)
            else:
                validation_run.progress = -1
            validation_run.save()
            __logger.info(
                "Dealt with task {}, validation {} is {} % done...".format(
                    async_result.id, validation_run.id,
                    validation_run.progress))

        # once all tasks are finished:
        # only store parameters and produce graphs if validation wasn't cancelled and
        # we have metrics for at least one gpi - otherwise no netcdf output file

        if (not validation_aborted):
            set_outfile(validation_run, run_dir)

            iam_dict = define_intra_annual_metrics(validation_run)
            temp_sub_wdw_instance = iam_dict['temp_sub_wdw_instance']
            temp_sub_wdws = iam_dict['temp_sub_wdws']

            transcriber = Pytesmo2Qa4smResultsTranscriber(
                pytesmo_results=os.path.join(OUTPUT_FOLDER,
                                          validation_run.output_file.name),
                intra_annual_slices=temp_sub_wdw_instance,
                keep_pytesmo_ncfile=False)
            if transcriber.exists:
                restructured_results = transcriber.get_transcribed_dataset()
                transcriber.output_file_name = transcriber.build_outname(
                    run_dir, results.keys())
                transcriber.write_to_netcdf(transcriber.output_file_name)

                save_validation_config(validation_run)

                transcriber.compress(path=transcriber.output_file_name,
                                     compression='zlib',
                                     complevel=9)

                if temp_sub_wdws is None:
                    temporal_sub_windows_names = [DEFAULT_TSW]
                else:
                    temporal_sub_windows_names = temp_sub_wdw_instance.names

                __logger.info(
                    f'temporal_sub_windows_names: {temporal_sub_windows_names}'
                )

                generate_all_graphs(
                    validation_run=validation_run,
                    outfolder=run_dir,
                    temporal_sub_windows=temporal_sub_windows_names,
                    save_metadata=validation_run.plots_save_metadata)

    except Exception as e:
        __logger.exception('Unexpected exception during validation {}:'.format(
            validation_run))

    finally:
        validation_run.end_time = datetime.now(tzlocal())
        validation_run.save()
        __logger.info(
            "Validation finished: {}. Jobs: {}, Errors: {}, OK: {}, End time: {} "
            .format(validation_run, validation_run.total_points,
                    validation_run.error_points, validation_run.ok_points,
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
        app.control.revoke(str(task.celery_task_id))  # @UndefinedVariable
        task.delete()

    run_dir = os.path.join(OUTPUT_FOLDER, str(validation_run.id))
    if os.path.exists(run_dir):
        __logger.info('Validation got cancelled, so the result files should be cleaned.')
        for file_name in os.listdir(run_dir):
            if file_name.endswith('.nc'):
                file_path = os.path.join(run_dir, file_name)
                os.remove(file_path)

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
            if TEMPORAL_SUB_WINDOW_SEPARATOR in metric:
                prefix = metric.split(TEMPORAL_SUB_WINDOW_SEPARATOR)[0]
                metric = metric.split(TEMPORAL_SUB_WINDOW_SEPARATOR)[1]
            else:
                prefix = None
            # static 'metrics' (e.g. metadata, geoinfo) are not related to datasets
            statics = ["gpi", "lat", "lon"]
            statics.extend(METADATA_TEMPLATE["ismn_ref"])
            if metric in statics:
                new_key = metric
            else:
                datasets = list(map(lambda t: t[0], key))
                if metric[0] == '(' and metric[-1] == ')':
                    metric = ast.literal_eval(metric)   # casts the string representing a tuple to a real tuple
                if isinstance(metric, tuple):
                    # happens only for triple collocation metrics, where the
                    # metric key is a tuple of (metric, dataset)
                    # if metric[1].startswith("0-"):
                    #     # triple collocation metrics for the reference should
                    #     # not show up in the results
                    #     continue
                    new_metric = "_".join(metric)
                else:
                    new_metric = metric
                if prefix:
                    new_metric = f"{prefix}{TEMPORAL_SUB_WINDOW_SEPARATOR}{new_metric}"
                new_key = f"{new_metric}_between_{'_and_'.join(datasets)}"
            if prefix:
                metric = f"{prefix}{TEMPORAL_SUB_WINDOW_SEPARATOR}{metric}"
            qa4sm_res[qa4sm_key][new_key] = results[key][metric]
    return qa4sm_res


def _compare_param_filters(new_param_filters, old_param_filters):
    """
    Checking if parametrised filters are the same for given configuration, checks till finds the first failure
    or till the end of the list.

    If lengths of queries do not agree then return False.
    """
    if len(new_param_filters) != len(old_param_filters):
        return False
    else:
        ind = 0
        max_ind = len(new_param_filters)
        is_the_same = True
        while ind < max_ind and new_param_filters[
                ind].parameters == old_param_filters[ind].parameters:
            ind += 1
        if ind != len(new_param_filters):
            is_the_same = False

    return is_the_same


def _compare_filters(new_dataset, old_dataset):
    """
    Checking if filters are the same for given configuration, checks till finds the first failure or till the end
     of the list. If filters are the same, then parameterised filters are checked.

    If lengths of queries do not agree then return False.
    """

    new_run_filters = new_dataset.filters.all().order_by('name')
    old_run_filters = old_dataset.filters.all().order_by('name')
    new_filts_len = len(new_run_filters)
    old_filts_len = len(old_run_filters)

    if new_filts_len != old_filts_len:
        return False
    elif new_filts_len == old_filts_len == 0:
        is_the_same = True
        new_param_filters = new_dataset.parametrisedfilter_set.all().order_by(
            'filter_id')
        if len(new_param_filters) != 0:
            old_param_filters = old_dataset.parametrisedfilter_set.all(
            ).order_by('filter_id')
            is_the_same = _compare_param_filters(new_param_filters,
                                                 old_param_filters)
        return is_the_same
    else:
        filt_ind = 0
        max_filt_ind = new_filts_len

        while filt_ind < max_filt_ind and new_run_filters[
                filt_ind] == old_run_filters[filt_ind]:
            filt_ind += 1

        if filt_ind == max_filt_ind:
            is_the_same = True
            new_param_filters = new_dataset.parametrisedfilter_set.all(
            ).order_by('filter_id')
            if len(new_param_filters) != 0:
                old_param_filters = old_dataset.parametrisedfilter_set.all(
                ).order_by('filter_id')
                is_the_same = _compare_param_filters(new_param_filters,
                                                     old_param_filters)
        else:
            is_the_same = False
    return is_the_same


def _compare_datasets(new_run_config, old_run_config):
    """
    Takes queries of dataset configurations and compare datasets one by one. If names and versions agree,
    checks filters.

    Runs till the first failure or til the end of the configuration list.
    If lengths of queries do not agree then return False.
    """
    new_len = len(new_run_config)

    if len(old_run_config) != new_len:
        return False
    else:
        ds_fields = DS_FIELDS
        max_ds_ind = len(ds_fields)
        the_same = True
        conf_ind = 0

        while conf_ind < new_len and the_same:
            ds_ind = 0
            new_dataset = new_run_config[conf_ind]
            old_dataset = old_run_config[conf_ind]
            while ds_ind < max_ds_ind and getattr(
                    new_dataset, ds_fields[ds_ind]) == getattr(
                        old_dataset, ds_fields[ds_ind]):
                ds_ind += 1
            if ds_ind == max_ds_ind:
                the_same = _compare_filters(new_dataset, old_dataset)
            else:
                the_same = False
            conf_ind += 1
    return the_same


def _check_scaling_method(new_run, old_run):
    """
    It takes two validation runs and compares scaling method together with the scaling reference dataset.

    """
    new_run_sm = new_run.scaling_method
    if new_run_sm != old_run.scaling_method:
        return False
    else:
        if new_run_sm != 'none':
            try:
                new_scal_ref = DatasetConfiguration.objects.get(
                    pk=new_run.scaling_ref_id).dataset
                run_scal_ref = DatasetConfiguration.objects.get(
                    pk=old_run.scaling_ref_id).dataset
                if new_scal_ref != run_scal_ref:
                    return False
            except:
                return False
    return True


def compare_validation_runs(new_run, runs_set, user):
    """
    Compares two validation runs. It takes a new_run and checks the query given by runs_set according to parameters
    given in the vr_fileds. If all fields agree it checks datasets configurations.

    It works till the first found validation run or till the end of the list.

    Returns a dict:
         {
        'is_there_validation': is_the_same,
        'val_id': val_id
        }
        where is_the_same migh be True or False and val_id might be None or the appropriate id ov a validation run
    """
    vr_fields = VR_FIELDS
    is_the_same = False  # set to False because it looks for the first found validation run
    is_published = False
    old_user = None
    max_vr_ind = len(vr_fields)
    max_run_ind = len(runs_set)
    run_ind = 0
    while not is_the_same and run_ind < max_run_ind:
        run = runs_set[run_ind]
        ind = 0
        while ind < max_vr_ind and getattr(run, vr_fields[ind]) == getattr(
                new_run, vr_fields[ind]):
            ind += 1
        if ind == max_vr_ind and _check_scaling_method(new_run, run):
            new_run_config = DatasetConfiguration.objects.filter(
                validation=new_run).order_by('dataset')
            old_run_config = DatasetConfiguration.objects.filter(
                validation=run).order_by('dataset')
            is_the_same = _compare_datasets(new_run_config, old_run_config)
            val_id = run.id
            is_published = run.doi != ''
            old_user = run.user
        run_ind += 1

    val_id = None if not is_the_same else val_id
    response = {
        'is_there_validation': is_the_same,
        'val_id': val_id,
        'belongs_to_user': old_user == user,
        'is_published': is_published
    }
    return response


def copy_validationrun(run_to_copy, new_user):
    # checking if the new validation belongs to the same user:
    if run_to_copy.user == new_user:
        run_id = run_to_copy.id
        # belongs_to_user = True
    else:
        # copying validation
        valrun_user = CopiedValidations(used_by_user=new_user,
                                        original_run=run_to_copy)
        valrun_user.original_run_date = run_to_copy.start_time
        valrun_user.save()

        # old info which is needed then
        old_scaling_ref_id = run_to_copy.scaling_ref_id
        old_val_id = str(run_to_copy.id)
        old_val_name = run_to_copy.name_tag

        dataset_conf = DatasetConfiguration.objects.filter(
            validation=run_to_copy)

        run_to_copy.user = new_user
        run_to_copy.id = None
        run_to_copy.start_time = datetime.now(tzlocal())
        run_to_copy.end_time = datetime.now(tzlocal())
        # treating this validation as a brand new:
        run_to_copy.last_extended = None
        run_to_copy.is_archived = False
        run_to_copy.expiry_notified = False

        run_to_copy.name_tag = 'Copy of ' + old_val_name if old_val_name != '' else 'Copy of Unnamed Validation'
        run_to_copy.save()
        run_id = run_to_copy.id

        # adding the copied validation to the copied validation list
        valrun_user.copied_run = run_to_copy
        valrun_user.save()

        # new configuration
        for conf in dataset_conf:
            old_id = conf.id
            old_filters = conf.filters.all()
            old_param_filters = conf.parametrisedfilter_set.all()

            # setting new scaling reference id
            if old_id == old_scaling_ref_id:
                run_to_copy.scaling_ref_id = conf.id

            new_conf = conf
            new_conf.pk = None
            new_conf.validation = run_to_copy
            new_conf.save()

            # setting filters
            new_conf.filters.set(old_filters)
            if len(old_param_filters) != 0:
                for param_filter in old_param_filters:
                    param_filter.id = None
                    param_filter.dataset_config = new_conf
                    param_filter.save()

        # the reference configuration is always the last one:
        try:
            run_to_copy.spatial_reference_configuration_id = conf.id
            run_to_copy.save()
        except:
            pass

        # copying files
        # new directory -> creating if doesn't exist
        new_dir = os.path.join(OUTPUT_FOLDER, str(run_id))
        mkdir_if_not_exists(new_dir)
        # old directory and all files there
        old_dir = os.path.join(OUTPUT_FOLDER, old_val_id)

        if os.path.isdir(old_dir):
            old_files = os.listdir(old_dir)
            if len(old_files) != 0:
                for file_name in old_files:
                    new_file = new_dir + '/' + file_name
                    old_file = old_dir + '/' + file_name
                    try:
                        copy2(old_file, new_file)
                    except IsADirectoryError as e:
                        copytree(
                            old_file, new_file
                        )  # with the restructuring of netCDF files, all graphics etc are now stored in dedicated directories
                    if '.nc' in new_file:
                        run_to_copy.output_file = str(run_id) + '/' + file_name
                        run_to_copy.save()
                        file = netCDF4.Dataset(new_file,
                                               mode='a',
                                               format="NETCDF4")

                        new_url = settings.SITE_URL + get_angular_url(
                            'result', run_id)
                        file.setncattr('url', new_url)
                        file.setncattr(
                            'date_copied',
                            run_to_copy.start_time.strftime('%Y-%m-%d %H:%M'))
                        file.close()

    response = {
        'run_id': run_id,
    }
    return response


def get_period(val_run: ValidationRun) -> Union[None, List[str]]:
    '''
    Extract the validation period from the validation run object.

    Parameters
    ----------
    val_run : ValidationRun
        The validation run object

    Returns
    -------
    Union[None, List[str]]
        The validation period as a list of two strings, the start and end date, respectively. If no period is defined, None is returned.
    '''
    if val_run.interval_from is not None and val_run.interval_to is not None:
        # while pytesmo can't deal with timezones, normalise the validation period to utc; can be removed once pytesmo can do timezones
        startdate = val_run.interval_from.astimezone(UTC).replace(
            tzinfo=None)
        enddate = val_run.interval_to.astimezone(UTC).replace(
            tzinfo=None)
        return [startdate, enddate]
    return None

def define_intra_annual_metrics(val_run: ValidationRun) -> Dict[str, Union[TemporalSubWindowsCreator, Dict[str, TsDistributor], None]]:
    '''
    Extract the intra-annual metrics settings from the validation run and instantiate the corresponding objects.

    Parameters
    ----------
    val_run : ValidationRun
        The validation run object

    Returns
    -------
    Dict[str, Union[TemporalSubWindowsCreator, Dict[str, TsDistributor], None]]
        A dictionary containing the temporal sub-window instance and the custom temporal sub-windows, if applicable. Otherwise, filled with None.
    '''
    # per default, assume bulk case
    temp_sub_wdw_instance = None
    temp_sub_wdws = None

    # in case intra-annual metrics are desired, instantiate corresponding object
    if val_run.intra_annual_metrics:
        intra_annual_metric_lut = {'Seasonal': 'seasons',
                                'Monthly': 'months'}     #TODO implement properly in qa4sm_reader.globals

        temp_sub_wdw_instance = TemporalSubWindowsCreator(
            temporal_sub_window_type=intra_annual_metric_lut[val_run.intra_annual_type],
            overlap=int(val_run.intra_annual_overlap),
            custom_file=None)  # loading default temporal sub-windows from globals file

        period = get_period(val_run)
        if not period:
            period = [datetime(year=1978, month=1, day=1), datetime.now()]    #NOTE bit of a hack, but we need a period for the default case

        default_temp_sub_wndw = NewSubWindow(DEFAULT_TSW, *period)
        temp_sub_wdw_instance.add_temp_sub_wndw(
            new_temp_sub_wndw=default_temp_sub_wndw,
            insert_as_first_wndw=True)  # always add the default case and make it as the first one (wrong order will throw errors later on)
        temp_sub_wdws = temp_sub_wdw_instance.custom_temporal_sub_windows

    __logger.debug(f"{temp_sub_wdw_instance=}")
    __logger.debug(f"{temp_sub_wdws=}")
    return {'temp_sub_wdw_instance': temp_sub_wdw_instance, 'temp_sub_wdws': temp_sub_wdws}
