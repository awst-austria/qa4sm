import logging
from datetime import datetime
from os import path
from re import sub as regex_sub

from django.conf import settings

from valentina.celery import app

from celery.app import shared_task
from dateutil.tz import tzlocal
from netCDF4 import Dataset
from pytesmo.validation_framework.results_manager import netcdf_results_manager
from pytesmo.validation_framework.validation import Validation

import numpy as np
from validator.mailer import send_val_done_notification
from validator.metrics import EssentialMetrics
from validator.models import ValidationRun


from validator.validation.util import mkdir_if_not_exists, first_file_in
from validator.validation.globals import OUTPUT_FOLDER
from validator.validation.readers import create_reader
from validator.validation.filters import setup_filtering
from validator.validation.batches import create_jobs
from validator.validation.graphics import generate_all_graphs


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
    __logger.debug("Executing validation {}, job: {}".format(validation_id, job))
    start_time = datetime.now(tzlocal())
    try:
        validation_run = ValidationRun.objects.get(pk=validation_id)
        val = create_pytesmo_validation(validation_run)
        result = val.calc(*job)
        end_time = datetime.now(tzlocal())
        duration = end_time - start_time
        duration = (duration.days * 86400) + (duration.seconds)
        numgpis = num_gpis_from_job(job)
        __logger.debug("Finished job {} in validation {}, took {} seconds for {} gpis".format(job, validation_id, duration, numgpis))
        return {'result':result,'job':job}
    except Exception as e:
        self.retry(countdown=2, exc=e)

def check_and_store_results(validation_run, job, results, save_path):
    __logger.debug(job)

    if len(results) < 1:
        __logger.warn('Potentially problematic job: {} - no results'.format(job))
        return

    if np.isnan(next(iter(results.values()))['R'][0]):
        __logger.warn('Potentially problematic job: {} - R is nan'.format(job))

    netcdf_results_manager(results, save_path)

def run_validation(validation_id):
    validation_run = ValidationRun.objects.get(pk=validation_id)


    if (hasattr(settings, 'CELERY_TASK_ALWAYS_EAGER')==False) or (settings.CELERY_TASK_ALWAYS_EAGER==False):
        app.control.add_consumer(validation_run.user.username, reply=True)

    try:
        __logger.info("Starting validation: {}".format(validation_id))

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
            job_id = execute_job.apply_async(args=[validation_id, j], queue=validation_run.user.username)
            #job_id = execute_job.delay(validation_id, j)
            async_results.append(job_id)
            job_table[job_id] = j

        executed_jobs = 0
        for async_result in async_results:
            try:
                result_dict=async_result.get() # calling result.AsyncResult.get
                async_result.forget()
                results = result_dict['result']
                job = result_dict['job']
                check_and_store_results(validation_run, job, results, save_path)
                validation_run.ok_points += num_gpis_from_job(job_table[async_result])
            except Exception:
                validation_run.error_points += num_gpis_from_job(job_table[async_result])
                __logger.exception('Celery could not execute the job. Job ID: {} Error: {}'.format(async_result.id,async_result.info))
            finally:
                executed_jobs +=1
                validation_run.progress=round(((validation_run.ok_points + validation_run.error_points)/validation_run.total_points)*100)
                validation_run.save()
                __logger.info("Validation {} is {} % done...".format(validation_run.id, validation_run.progress))

        set_outfile(validation_run, run_dir)
        validation_run.save() # let's save before we do anything else...

        # only store parameters and produce graphs if we have metrics for at least one gpi - otherwise no netcdf output file
        if validation_run.ok_points > 0:
            save_validation_config(validation_run)
            generate_all_graphs(validation_run, run_dir)

    except Exception:
        __logger.exception('Unexpected exception during validation {}:'.format(validation_run))

    finally:
        validation_run.end_time = datetime.now(tzlocal())
        __logger.info("Validation finished: {}. Jobs: {}, Errors: {}, OK: {}".format(
            validation_run, validation_run.total_points, validation_run.error_points, validation_run.ok_points))
        if (validation_run.error_points + validation_run.ok_points) != validation_run.total_points:
            __logger.warn("Caution, # of gpis, # of errors, and # of OK points don't match!")
        validation_run.save()

        send_val_done_notification(validation_run)

    return validation_run
