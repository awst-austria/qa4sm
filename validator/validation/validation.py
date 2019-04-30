from datetime import datetime
import logging
from os import path
from re import sub as regex_sub
import uuid

from celery.app import shared_task
from dateutil.tz import tzlocal
from django.conf import settings
from netCDF4 import Dataset
from pytesmo.validation_framework.metric_calculators import IntercomparisonMetrics, get_dataset_names
from pytesmo.validation_framework.results_manager import netcdf_results_manager
from pytesmo.validation_framework.validation import Validation

import numpy as np
from valentina.celery import app
from validator.mailer import send_val_done_notification
from validator.models import ValidationRun
from validator.models.celery_task import CeleryTask
from validator.validation.batches import create_jobs
from validator.validation.filters import setup_filtering
from validator.validation.globals import OUTPUT_FOLDER
from validator.validation.graphics import generate_all_graphs
from validator.validation.readers import create_reader
from validator.validation.util import mkdir_if_not_exists, first_file_in
from pytesmo.validation_framework.data_manager import DataManager


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

        for i, dataset_config in enumerate(validation_run.dataset_configurations.all()):
            if dataset_config.filters.all():
                filters = '; '.join([x.description for x in dataset_config.filters.all()])
            else:
                filters = 'N/A'

            ds.setncattr('val_dc_dataset' + str(i), dataset_config.dataset.short_name)
            ds.setncattr('val_dc_version' + str(i), dataset_config.version.short_name)
            ds.setncattr('val_dc_variable' + str(i), dataset_config.variable.short_name)
            ds.setncattr('val_dc_filters' + str(i), filters)

            if ((validation_run.reference_configuration is not None) and
                (dataset_config.id == validation_run.reference_configuration.id)):
                ds.val_ref = 'val_dc_dataset' + str(i)

            if ((validation_run.scaling_ref is not None) and
                (dataset_config.id == validation_run.scaling_ref.id)):
                ds.val_scaling_ref = 'val_dc_dataset' + str(i)

        ds.val_scaling_method=validation_run.scaling_method
        ds.close()
    except Exception:
        __logger.exception('Validation configuration could not be stored.')

def create_pytesmo_validation(validation_run):
    ds_list = []
    ref_name = None
    scaling_ref_name = None
    for ds_num, dataset_config in enumerate(validation_run.dataset_configurations.all(), start=1):
        reader = create_reader(dataset_config.dataset, dataset_config.version)
        reader = setup_filtering(reader, list(dataset_config.filters.all()), dataset_config.dataset, dataset_config.variable)
        dataset_name = '{}-{}'.format(ds_num, dataset_config.dataset.short_name)
        ds_list.append( (dataset_name, {'class': reader, 'columns': [dataset_config.variable.pretty_name]}) )

        if ((validation_run.reference_configuration) and
            (dataset_config.id == validation_run.reference_configuration.id)):
            ref_name = dataset_name
        if ((validation_run.scaling_ref) and
            (dataset_config.id == validation_run.scaling_ref.id)):
            scaling_ref_name = dataset_name

    datasets=dict(ds_list)
    ds_num = len(ds_list)

    period = None
    if validation_run.interval_from is not None and validation_run.interval_to is not None:
        period = [validation_run.interval_from, validation_run.interval_to]

    datamanager = DataManager(datasets, ref_name=ref_name, period=period)
    ds_names = get_dataset_names(datamanager.reference_name, datamanager.datasets, n=ds_num)
    metrics = IntercomparisonMetrics(dataset_names=ds_names, other_names=['k{}'.format(i + 1) for i in range(ds_num-1)])

    val = Validation(
        datasets=datamanager,
        spatial_ref=ref_name,
        temporal_window=0.5,
        scaling=validation_run.scaling_method,
        scaling_ref=scaling_ref_name,
        metrics_calculators={(ds_num, ds_num): metrics.calc_metrics},
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
        __logger.warning('Potentially problematic job: {} - no results'.format(job))
        return

    netcdf_results_manager(results, save_path)

def run_validation(validation_id):
    validation_run = ValidationRun.objects.get(pk=validation_id)
    validation_aborted_flag=False;


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
            async_results.append(job_id)
            job_table[job_id] = j
            celery_task=CeleryTask()
            celery_task.validation=validation_run
            celery_task.celery_task_id=uuid.UUID(job_id.id).hex
            celery_task.save()

        executed_jobs = 0
        for async_result in async_results:
            try:
                while True:
                    try:
                        result_dict=async_result.get(timeout=10) # calling result.AsyncResult.get
                        async_result.forget()
                        break
                    except Exception as e:
                        if e.__class__.__name__ != 'TimeoutError':
                            raise e

                        try:
                            celery_task=CeleryTask.objects.get(celery_task_id=uuid.UUID(async_result.id).hex)
                            __logger.debug('Celery task timeout. Continue...')
                        except Exception:
                            __logger.debug('Validation got cancelled')
                            validation_aborted_flag=True
                            validation_run.progress=-1
                            validation_run.save()
                            return validation_run
                    finally:
                        try:
                            celery_task=CeleryTask.objects.get(celery_task_id=uuid.UUID(async_result.id).hex)
                            celery_task.delete()
                        except Exception:
                            __logger.debug('Celery task does not exists. Validation run: {} Celery task ID: {} - {}'.format(validation_id,
                                                                                                                       async_result.id,uuid.UUID(async_result.id).hex))

                results = result_dict['result']
                job = result_dict['job']
                check_and_store_results(validation_run, job, results, save_path)
                validation_run.ok_points += num_gpis_from_job(job_table[async_result])
            except Exception:
                validation_run.error_points += num_gpis_from_job(job_table[async_result])
                __logger.exception('Celery could not execute the job. Job ID: {} Error: {}'.format(async_result.id,async_result.info))
            finally:
                if validation_aborted_flag:
                    return
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
        validation_run.save()
        __logger.info("Validation finished: {}. Jobs: {}, Errors: {}, OK: {}, End time: {} ".format(
            validation_run, validation_run.total_points, validation_run.error_points, validation_run.ok_points,validation_run.end_time))
        if validation_aborted_flag==False:
            if (validation_run.error_points + validation_run.ok_points) != validation_run.total_points:
                __logger.warn("Caution, # of gpis, # of errors, and # of OK points don't match!")
                validation_run.save()

            send_val_done_notification(validation_run)

    print('Valrun: {}'.format(validation_run))
    return validation_run

def stop_running_validation(validation_id):
    __logger.info("Stopping validation {}".format(validation_id))
    validation_run = ValidationRun.objects.get(pk=validation_id)
    validation_run.progress=-1
    validation_run.save()

    celery_tasks=CeleryTask.objects.filter(validation=validation_run)

    for task in celery_tasks:
        app.control.revoke(task.celery_task)
        task.delete()


