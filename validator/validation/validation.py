import logging
from datetime import datetime
from os import path
from re import sub as regex_sub
import uuid

from django.conf import settings

from valentina.celery import app

from celery.app import shared_task
from celery.exceptions import TaskRevokedError, TimeoutError
from dateutil.tz import tzlocal
from netCDF4 import Dataset
from pytesmo.validation_framework.results_manager import netcdf_results_manager
from pytesmo.validation_framework.validation import Validation

from validator.mailer import send_val_done_notification
from validator.metrics import EssentialMetrics
from validator.models import ValidationRun

from validator.validation.util import mkdir_if_not_exists, first_file_in
from validator.validation.globals import OUTPUT_FOLDER
from validator.validation.readers import create_reader
from validator.validation.filters import setup_filtering
from validator.validation.batches import create_jobs
from validator.validation.graphics import generate_all_graphs
from validator.models.celery_task import CeleryTask


__logger = logging.getLogger(__name__)


def set_outfile(validation_run, run_dir):
    outfile = first_file_in(run_dir, '.nc')
    if outfile is not None:
        outfile = regex_sub('/?' + OUTPUT_FOLDER + '/?', '', outfile)
        validation_run.output_file.name = outfile

def save_validation_config(validation_run):
    try:
        ds = Dataset(path.join(OUTPUT_FOLDER, validation_run.output_file.name), "a", format="NETCDF4")
        if(validation_run.interval_from is None):
            ds.val_interval_from="N/A"
        else:
            ds.val_interval_from=validation_run.interval_from.strftime('%Y-%m-%d %H:%M')

        if(validation_run.interval_to is None):
            ds.val_interval_to="N/A"
        else:
            ds.val_interval_to=validation_run.interval_to.strftime('%Y-%m-%d %H:%M')

        if validation_run.data_filters.all():
            ds.val_data_filters = '; '.join([x.description for x in validation_run.data_filters.all()])
        else:
            ds.val_data_filters = 'N/A'

        if validation_run.ref_filters.all():
            ds.val_ref_filters = '; '.join([x.description for x in validation_run.ref_filters.all()])
        else:
            ds.val_ref_filters = 'N/A'

        ds.val_data_dataset=validation_run.data_dataset.pretty_name
        ds.val_data_version=validation_run.data_version.pretty_name
        ds.val_data_variable=validation_run.data_variable.pretty_name
        ds.val_ref_dataset=validation_run.ref_dataset.pretty_name
        ds.val_ref_version=validation_run.ref_version.pretty_name
        ds.val_ref_variable=validation_run.ref_variable.pretty_name

        ds.val_scaling_ref=validation_run.scaling_ref
        ds.val_scaling_method=validation_run.scaling_method
        ds.close()
    except Exception:
        __logger.exception('Validation configuration could not be stored.')

def create_pytesmo_validation(validation_run):
    data_reader = create_reader(validation_run.data_dataset, validation_run.data_version)
    ref_reader = create_reader(validation_run.ref_dataset, validation_run.ref_version)

    data_reader = setup_filtering(data_reader, list(validation_run.data_filters.all()), validation_run.data_dataset, validation_run.data_variable)
    ref_reader = setup_filtering(ref_reader, list(validation_run.ref_filters.all()), validation_run.ref_dataset, validation_run.ref_variable)

    datasets = {
            validation_run.ref_dataset.short_name: {
                'class': ref_reader,
                'columns': [validation_run.ref_variable.pretty_name]
                },
            validation_run.data_dataset.short_name: {
                'class': data_reader,
                'columns': [validation_run.data_variable.pretty_name]
                }}

    period = None
    if validation_run.interval_from is not None and validation_run.interval_to is not None:
        period = [validation_run.interval_from, validation_run.interval_to]

    metrics = EssentialMetrics()

    if validation_run.scaling_ref == ValidationRun.SCALE_REF:
        scaling_ref=validation_run.data_dataset.short_name ## if you scale the reference dataset, the scaling reference is the normal dataset %-P
    else:
        scaling_ref=validation_run.ref_dataset.short_name

    val = Validation(
            datasets,
            spatial_ref=validation_run.ref_dataset.short_name,
            temporal_ref=validation_run.data_dataset.short_name,
            temporal_window=0.5,
            scaling=validation_run.scaling_method,
            scaling_ref=scaling_ref,
            metrics_calculators={(2, 2): metrics.calc_metrics},
            period=period)

    return val

def num_gpis_from_job(job):
    try:
        num_gpis = len(job[0])
    except:
        num_gpis = 1

    return num_gpis

@shared_task(bind=True,max_retries=3)
def execute_job(self,validation_id, job):
    task_id = execute_job.request.id
    numgpis = num_gpis_from_job(job)
    __logger.debug("Executing job {} from validation {}, # of gpis: {}".format(task_id, validation_id, numgpis))
    start_time = datetime.now(tzlocal())
    try:
        validation_run = ValidationRun.objects.get(pk=validation_id)
        val = create_pytesmo_validation(validation_run)
        result = val.calc(*job)
        end_time = datetime.now(tzlocal())
        duration = end_time - start_time
        duration = (duration.days * 86400) + (duration.seconds)
        __logger.debug("Finished job {} from validation {}, took {} seconds for {} gpis".format(task_id, validation_id, duration, numgpis))
        return result
    except Exception as e:
        self.retry(countdown=2, exc=e)

def check_and_store_results(job_id, results, save_path):
    if len(results) < 1:
        __logger.warn('Potentially problematic job: {} - no results'.format(job_id))
        return

    netcdf_results_manager(results, save_path)

def track_celery_task(validation_run, task_id):
    celery_task=CeleryTask()
    celery_task.validation=validation_run
    celery_task.celery_task=uuid.UUID(task_id).hex
    celery_task.save()

def celery_task_cancelled(task_id):
    ## stop_running_validation deletes the validation's tasks from the db. so if they don't exist in the db the task was cancelled
    return not CeleryTask.objects.filter(celery_task = task_id).exists()

def untrack_celery_task(task_id):
    try:
        celery_task=CeleryTask.objects.get(celery_task=task_id)
        celery_task.delete()
    except CeleryTask.DoesNotExist:
        __logger.debug('Task {} already deleted from db.'.format(task_id))

def run_validation(validation_id):
    __logger.info("Starting validation: {}".format(validation_id))
    validation_run = ValidationRun.objects.get(pk=validation_id)
    validation_aborted = False;

    if ((not hasattr(settings, 'CELERY_TASK_ALWAYS_EAGER')) or (not settings.CELERY_TASK_ALWAYS_EAGER)):
        app.control.add_consumer(validation_run.user.username, reply=True)  # @UndefinedVariable

    try:
        run_dir = path.join(OUTPUT_FOLDER, str(validation_run.id))
        mkdir_if_not_exists(run_dir)

        total_points, jobs = create_jobs(validation_run)
        validation_run.total_points = total_points
        validation_run.save() # save the number of gpis before we start

        __logger.debug("Jobs to run: {}".format(jobs))

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
                if not validation_aborted: ## only wait for this task if the validation hasn't been cancelled
                    task_running = True
                    while task_running: ## regularly check if the validation has been cancelled in this loop, otherwise we wouldn't notice
                        try:
                            results = async_result.get(timeout=10) ## this throws TimeoutError after waiting 10 secs or TaskRevokedError if revoked before starting
                            ## if we got here, the task is finished now
                            task_running = False ## stop looping because task finished
                            if celery_task_cancelled(async_result.id): ## we can still have a cancelled validation that took less than 10 secs
                                validation_aborted = True
                            else:
                                untrack_celery_task(async_result.id)

                        except (TimeoutError, TaskRevokedError) as te:
                            ## see if our task got cancelled - if not, just continue loop
                            if celery_task_cancelled(async_result.id):
                                task_running = False ## stop looping because we aborted
                                validation_aborted = True
                                __logger.debug('Validation got cancelled, dropping task {}: {}'.format(async_result.id, te))

                if validation_aborted:
                    validation_run.error_points += num_gpis_from_job(job_table[async_result.id])
                else:
                    check_and_store_results(async_result.id, results, save_path)
                    validation_run.ok_points += num_gpis_from_job(job_table[async_result.id])

            except Exception:
                validation_run.error_points += num_gpis_from_job(job_table[async_result.id])
                __logger.exception('Celery could not execute the job. Job ID: {} Error: {}'.format(async_result.id, async_result.info))
            finally:
                # whether finished or cancelled or failed, forget about this task now
                async_result.forget()

            if not validation_aborted:
                validation_run.progress = round(((validation_run.ok_points + validation_run.error_points)/validation_run.total_points)*100)
            else:
                validation_run.progress = -1
            validation_run.save()
            __logger.info("Dealt with task {}, validation {} is {} % done...".format(async_result.id, validation_run.id, validation_run.progress))

        # once all tasks are finished:
        # only store parameters and produce graphs if validation wasn't cancelled and
        # we have metrics for at least one gpi - otherwise no netcdf output file
        if ((not validation_aborted) and (validation_run.ok_points > 0)):
            set_outfile(validation_run, run_dir)
            validation_run.save()
            save_validation_config(validation_run)
            generate_all_graphs(validation_run, run_dir)

    except Exception:
        __logger.exception('Unexpected exception during validation {}:'.format(validation_run))

    finally:
        validation_run.end_time = datetime.now(tzlocal())
        validation_run.save()
        __logger.info("Validation finished: {}. Jobs: {}, Errors: {}, OK: {}, End time: {} ".format(
            validation_run, validation_run.total_points, validation_run.error_points, validation_run.ok_points,validation_run.end_time))

        send_val_done_notification(validation_run)

    return validation_run

def stop_running_validation(validation_id):
    __logger.info("Stopping validation {} ".format(validation_id))
    validation_run = ValidationRun.objects.get(pk=validation_id)
    validation_run.progress=-1
    validation_run.save()

    celery_tasks=CeleryTask.objects.filter(validation=validation_run)

    for task in celery_tasks:
        app.control.revoke(task.celery_task)  # @UndefinedVariable
        task.delete()
