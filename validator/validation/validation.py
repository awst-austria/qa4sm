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
from pytesmo.validation_framework.data_manager import DataManager, get_result_combinations
from pytesmo.validation_framework.metric_calculators import (
    get_dataset_names,
    PairwiseIntercomparisonMetrics,
    TripleCollocationMetrics,
)
from pytesmo.validation_framework.temporal_matchers import (
    make_combined_temporal_matcher, )
import pandas as pd
import xarray as xr
import numpy as np
import warnings
from pytesmo.validation_framework.results_manager import netcdf_results_manager, build_filename
from pytesmo.validation_framework.validation import Validation
from pytesmo.validation_framework.metric_calculators_adapters import SubsetsMetricsAdapter, TsDistributor
import pytesmo.validation_framework.error_handling as eh

from pytz import UTC
import pytz

from valentina.celery import app

from api.frontend_urls import get_angular_url

from validator.mailer import send_val_done_notification
from validator.models import CeleryTask, DatasetConfiguration, CopiedValidations
from validator.models import ValidationRun, DatasetVersion
from validator.validation.batches import create_jobs, create_upscaling_lut
from validator.validation.filters import setup_filtering
from validator.validation.globals import OUTPUT_FOLDER, IRREGULAR_GRIDS, VR_FIELDS, DS_FIELDS, ISMN, DEFAULT_TSW, \
    TEMPORAL_SUB_WINDOW_SEPARATOR, METRICS, TEMPORAL_SUB_WINDOWS, ONLY_WITH_REFERENCE
from validator.validation.graphics import generate_all_graphs
from validator.validation.readers import create_reader, adapt_timestamp
from validator.validation.util import mkdir_if_not_exists, first_file_in
from validator.validation.globals import START_TIME, END_TIME, METADATA_TEMPLATE
from validator.validation.adapters import StabilityMetricsAdapter
import qa4sm_reader
from qa4sm_reader.intra_annual_temp_windows import TemporalSubWindowsCreator, NewSubWindow, TemporalSubWindowsFactory
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


def set_outfile(validation_run, run_dir, val_type="temporal"):
    outfile = first_file_in(run_dir, '.nc', val_type=val_type)
    if val_type == "temporal":
        if outfile is not None:
            outfile = regex_sub('/?' + OUTPUT_FOLDER + '/?', '', outfile)
            validation_run.output_file.name = outfile
    elif val_type == "spatial":
        if outfile is not None:
            outfile = regex_sub('/?' + OUTPUT_FOLDER + '/?', '', outfile)
            validation_run.output_file_spatial.name = outfile


def save_validation_config(validation_run):
    try:
        with netCDF4.Dataset(os.path.join(OUTPUT_FOLDER,
                                          validation_run.output_file.name),
                             "a",
                             format="NETCDF4") as ds:

            ds.qa4sm_version = settings.APP_VERSION
            ds.qa4sm_reader_version = qa4sm_reader.__version__
            ds.qa4sm_env_url = settings.ENV_FILE_URL_TEMPLATE.format(
                settings.APP_VERSION)
            ds.url = settings.SITE_URL + get_angular_url(
                'result', validation_run.id)

            try:
                if hasattr(validation_run, 'spatial_reference_configuration'):
                    dataset = validation_run.spatial_reference_configuration.dataset
                    if dataset and hasattr(dataset, 'is_scattered_data'):
                        ds.val_is_scattered_data = str(
                            dataset.is_scattered_data)
            except (AttributeError, TypeError):
                pass
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
                        __logger.error(
                            f"Error in save_validation_config: {e}. {filters=}{_list_comp=}"
                        )
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
                    # same is true for user datasets
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


def create_pytesmo_validation(validation_run, val_type="temporal"):
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
        if val_type == "temporal":
            metadata_template = METADATA_TEMPLATE['ismn_ref']
        else:
            metadata_template = METADATA_TEMPLATE['other_ref']
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

    # TODO: this should be move to the api view
    if validation_run.intra_annual_metrics and validation_run.stability_metrics:
        raise ValueError(
            "Both intra_annual_metrics and stability_metrics cannot be True at the same time."
        )

    tsw_metrics = None
    temp_sub_wdws = None

    if validation_run.intra_annual_metrics:
        tsw_metrics = "intra_annual"
    elif validation_run.stability_metrics:
        tsw_metrics = "stability"

    if tsw_metrics:
        tsw_dict = define_tsw_metrics(validation_run, period)
        temp_sub_wdw_instance = tsw_dict['temp_sub_wdw_instance']
        temp_sub_wdws = tsw_dict['temp_sub_wdws']

        # Proceed only if temp_sub_wdws is a dictionary
        if isinstance(temp_sub_wdws, dict):
            if tsw_metrics == "intra_annual":
                # Set up Intra-annual metrics
                pairwise_metrics = SubsetsMetricsAdapter(
                    calculator=_pairwise_metrics,
                    subsets=temp_sub_wdw_instance.custom_temporal_sub_windows,
                    group_results="join",
                )

            elif tsw_metrics == "stability":
                # Set up Stability metrics
                pairwise_metrics = StabilityMetricsAdapter(
                    calculator=_pairwise_metrics,
                    subsets=temp_sub_wdw_instance.custom_temporal_sub_windows,
                    group_results="join",
                )

    else:
        # Default case when tsw_metrics is None
        if temp_sub_wdws is None:
            pairwise_metrics = _pairwise_metrics
        else:
            raise ValueError(
                f"Invalid value for temp_sub_wdws: {temp_sub_wdws}. "
                "Please specify either None or a custom temporal sub windowing function."
            )

    try:
        metric_calculators = {(ds_num, 2): pairwise_metrics.calc_metrics}
    except Exception as e:
        print(e)

    if (len(ds_names) >= 3) and (validation_run.tcol is True):
        _tcol_metrics = TripleCollocationMetrics(
            spatial_ref_name,
            metadata_template=metadata_template,
            bootstrap_cis=validation_run.bootstrap_tcol_cis)

        if isinstance(temp_sub_wdws, dict):
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
            pd.Timedelta(temporalwindow_size / 2, "h")),
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
        val = create_pytesmo_validation(validation_run, val_type="temporal")

        result = val.calc(*job,
                          rename_cols=False,
                          only_with_reference=ONLY_WITH_REFERENCE,
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

def get_val_dict(val, gpi_info):
    """Returns Dictionary containing all data of a Validation for one GPI.
    
    Parameters
    ----------
    val: ValidationRun
        The validation run object
    gpi_info: tuple
        Tuple containing (GPI, longitude, latitude, {meta_information})

    Returns
    -------
    df_dict: dictionary
        Dictionary containing data of Validation run for specified GPI

    Raises
    ------
    eh.DataManagerError
        If data retrieval for gpi fails
    eh.NoGpiDataError
        If retrieved data is empty
    """
    try:
        df_dict = val.data_manager.get_data(gpi_info[0], gpi_info[1], gpi_info[2])
    except Exception as e:
        raise eh.DataManagerError(
            f"Getting the data for gpi {gpi_info} failed with"
            f" error: {e}")   
    # if no data is available continue with the next gpi
    if len(df_dict) == 0:
        raise eh.NoGpiDataError(f"No data for gpi {gpi_info}")
    return df_dict

def arraydata_gpi(val, gpi_info):
    """
    Retrieves, matches, and scales data for a specific GPI during a validation run.

    This function performs the temporal matching of datasets, handles 
    insufficient data cases by generating dummy results, and applies 
    scaling if configured in the validation run. It also updates the 
    metadata dictionary with spatial coordinates.

    Parameters
    ----------
    val : ValidationRun
        The validation run object containing configuration, data managers, 
        and metric calculators.
    gpi_info : tuple
        Tuple containing (gpi, lon, lat, {meta_information}).

    Returns
    -------
    data : pd.DataFrame
        The processed and matched DataFrame containing the observations 
        for the specified GPI.
    gpi_info : dict
        The fourth element of the input tuple (meta_information), 
        now updated with 'gpi', 'lon', and 'lat' keys.

    Raises
    ------
    eh.NoTempMatchedDataError
        If no temporally matched data exists for the given dataset 
        combinations at this GPI.
    eh.ScalingError
        If the scaling process fails for the retrieved data.
    """
    # read ts
    df_dict = get_val_dict(val, gpi_info)
    # match ts
    try:
        matched = val.temp_matching(df_dict, val.temporal_ref)
    except Exception:
        raise eh.TemporalMatchingError(
            f"Temporal matching failed for gpi {gpi_info}!"
        )
    names = tuple([(k, val.data_manager.datasets[k]["columns"][0]) 
                   for k in val.data_manager.datasets.keys() if k in df_dict.keys()])
    data = val.get_data_for_result_tuple(matched, names)
    # SCALING
    data = data.rename(columns=lambda x: x[0])
    # check if there should be scaling, 
    # if the scaling dataset is in the data and 
    # if the data for the scaling dataset is not empty
    if val.scaling is not None and \
       val.scaling_ref in data.columns and \
       not data[val.scaling_ref].isnull().all():
        scaling_index = data.columns.tolist().index(
            val.scaling_ref
        )
        try:
            data = val.scaling.scale(
                data, scaling_index, gpi_info
            )
        except Exception as e:
            raise eh.ScalingError(f"Scaling failed for gpi {gpi_info} with error {e}!")

    gpi_info[3].update({"gpi":gpi_info[0], "lon":gpi_info[1], "lat":gpi_info[2]})
    return data, gpi_info
    
def build_xarray(job, val, keep_meta=True, handle_errors="ignore"):
    """
    Assembles a synchronized xarray Dataset from multiple GPI.

    This function iterates through a set of GPIs provided by a job and retrieves 
    the relevant data using `arraydata_gpi`. It performs a temporal union to 
    create a common time index and aligns disparate station data into a preallocated, 
    sparse-aware multidimensional structure.

    Parameters
    ----------
    job : iterable
        An iterable (e.g., a list of tuples) containing task information 
        that can be unpacked into `gpi_info`.
    val : ValidationRun
        The validation run object used for data retrieval and configuration.

    Returns
    -------
    ds_all : xr.Dataset
        A consolidated Dataset with dimensions ('date_time', 'gpi'). 
        Includes data variables aligned to the union of all timestamps 
        and coordinate metadata (lon, lat, etc.) mapped to the 'gpi' dimension.

    Raises
    ------
    eh.NoGpiDataError
        If data retrieval fails for a GPI and `handle_errors` is set to "raise",
        or if no valid GPI data is found at all.
    """
    gpis_meta = {}
    data_vars = list(val.data_manager.datasets.keys())
    gpis_data = {}
    time_key = "date_time"

    for gpi_info in zip(*job):
        try:
            data, gpi_info = arraydata_gpi(val, gpi_info)
        except Exception as e:
            if handle_errors == "raise":
                raise eh.NoGpiDataError(
                    f"Data retrieval failed for gpi {gpi_info} with error {e}!"
                )
            else:
                warnings.warn(f"Data retrieval failed for gpi {gpi_info} with error {e}!")
                continue
        

        # reset index so date_time becomes a regular column
        data.index.name = time_key  # ensure index is named 'date_time'
        data_reset = data.reset_index()

        # skip if empty or date_time column missing
        if data_reset.empty or time_key not in data_reset.columns:
            warnings.warn(
                f"No '{time_key}' column for gpi {gpi_info[3].get('gpi', '?')}, skipping"
            )
            continue

        gpis_meta[gpi_info[3]["gpi"]] = gpi_info[3]
        gpis_data[gpi_info[3]["gpi"]] = {c: data_reset[c] for c in data_reset.columns}

    # -- GUARD: nothing to build --
    if not gpis_data:
        raise eh.NoGpiDataError(
            "No valid GPI data found for this job — all GPIs were skipped."
        )

    # -- BUILDING XARRAY -- #
    # Build union time index across all GPIs
    full_time = pd.DatetimeIndex(
        sorted(set().union(*[d[time_key] for d in gpis_data.values()])),
        name=time_key
    )

    if len(full_time) == 0:
        raise eh.NoGpiDataError(
            "No valid timestamps found across all GPIs."
        )

    # Preallocate arrays
    n_stations = len(gpis_meta)
    shape = (len(full_time), n_stations)

    data_arrays = {var: np.full(shape, np.nan, dtype="float64") for var in data_vars}

    # Fill arrays with station data 
    for j, gpi in enumerate(gpis_data.keys()):
        dat = gpis_data[gpi]
        aligned_idx = full_time.get_indexer(dat[time_key])  # positions in full_time

        for var in data_vars:
            if var in dat.keys():
                values = dat[var].values.astype("float64")
                # only fill positions where alignment succeeded (aligned_idx >= 0)
                valid_mask = aligned_idx >= 0
                data_arrays[var][aligned_idx[valid_mask], j] = values[valid_mask]

    # Build final dataset 
    df_meta = pd.DataFrame.from_dict(gpis_meta, orient='index')
    df_meta.index.name = "gpi"
    ds_all = xr.Dataset(
        {var: ((time_key, "gpi"), arr) for var, arr in data_arrays.items()},
        coords={
            time_key: full_time,
            "gpi": df_meta.index.values,
        }
    )
    if keep_meta:
        for col in df_meta.columns:
            # Use .values to ensure we pass the underlying numpy/object array
            ds_all.coords[str(col)] = ("gpi", df_meta[col].values)
    return ds_all

def get_spatial_meta(ds_use, time, metakeys):
    """
    Extracts specific metadata variables for a given timestamp across all GPIs.

    Parameters
    ----------
    ds_use : xr.Dataset
        The input dataset containing spatial and temporal data.
    time : numpy.datetime64 or xr.DataArray
        The specific timestep for which to retrieve metadata.
    metakeys : list of str
        The names of the variables in ds_use to be extracted as metadata.

    Returns
    -------
    date_meta : dict
        A dictionary where keys are the variable names and values are 
        NumPy arrays containing the metadata for all stations at that timestep.
    """
    date_meta = {k:ds_use.sel(date_time=time)[k].values for k in metakeys}
    return date_meta

def compact_results(results):
    """
    Converts a list of result dictionaries into a dictionary of NumPy arrays.

    This function "stacks" individual metric results collected over multiple 
    timesteps into a contiguous format, making them suitable for conversion 
    into xarray DataArrays or pandas DataFrames.

    Parameters
    ----------
    results : dict
        A dictionary where keys are dataset combinations (tuples) and 
        values are lists of dictionaries containing calculated metrics.

    Returns
    -------
    c_results : dict
        A dictionary with the same keys, where each metric field is 
        represented as a NumPy array instead of a list.
    """

    # Changed logic massively increased performance
    c_results = {}
    for key, result_list in results.items():
        c_results[key] = {}
        first_res = result_list[0]
        
        for field_name, first_val in first_res.items():
            entries = [np.atleast_1d(res[field_name])[0] for res in result_list]   
            c_results[key][field_name] = np.array(entries, dtype=first_val.dtype)
    return c_results

def spatial_validation_xr(val, ds_use, only_with_reference=True, handle_errors="ignore", validation_run=None):
    """
    Performs a spatial validation by calculating metrics for every timestep.

    Instead of calculating metrics across time for a single GPI, this function 
    iterates through the 'date_time' dimension and calculates metrics across 
    all available GPIs (stations) for each timestamp. This is typically used 
    to generate spatial performance maps or to analyze how validation 
    agreement changes over time.

    Parameters
    ----------
    val : ValidationRun
        The validation run object used for data retrieval and configuration.
    ds_use : xr.Dataset
        The consolidated dataset with dimensions ('date_time', 'gpi').
    only_with_reference: bool, optional (default: True)
        Only compute metrics for dataset combinations where the reference
        is included.

    Returns
    -------
    c_results : dict
        Compacted validation results containing the metrics for each 
        dataset combination, indexed by time.

    Raises
    ------
    eh.NoTempMatchedDataError
        If no data is found for a specific combination and error handling 
        is set to 'raise'.
    eh.MetricsCalculationError
        If the metrics calculator fails and error handling is set to 'raise'.

    Notes
    -----
    - The 'gpi_info' passed to the calculator is modified to represent a 
      temporal slice rather than a spatial point.
    """

    results = {}
    gpi_n_use_dict = {} # used to count number each gpi is used

    all_combinations = {}
    for n, k in val.metrics_c:
        combos = list(get_result_combinations(val.data_manager.ds_dict, n=k))
        for c in combos:
            c_list = [j[0] for j in c]
            if only_with_reference and val.data_manager.reference_name not in c_list:
                continue
            all_combinations[c] = (c_list, val.metrics_c[(n, k)])
            if c not in gpi_n_use_dict:
                gpi_n_use_dict[c] = {gpi: 0 for gpi in ds_use.gpi.values}
    df_all = ds_use.to_dataframe()

    total_times = len(ds_use.date_time)
    SAVE_INTERVAL = max(1, total_times // 100)  # save progress

    for i, time_val in enumerate(ds_use.date_time):
        try:
            result = {}
            # Slicing the pre-computed DataFrame is faster than xarray .sel().values
            df_date = df_all.xs(time_val.values, level='date_time')
            
            date_meta = get_spatial_meta(ds_use, time_val, metakeys=[])
            date_info = (0, 0, 0, date_meta)
            time_np = time_val.values

            for c, (c_list, metrics_calculator) in all_combinations.items():
                res_list = result.setdefault(c, [])
                
                # Efficient dropping and counting
                df_comb = df_date[c_list].dropna()
                
                # Update GPI counts in bulk
                current_gpi_counts = gpi_n_use_dict[c]
                for gpi in df_comb.index:
                    current_gpi_counts[gpi] += 1

                if df_comb.empty:
                    if handle_errors == "raise":
                        raise eh.NoTempMatchedDataError(f"Empty data for {c}")
                    metrics = metrics_calculator(pd.DataFrame(columns=c_list), date_info)
                    metrics["status"][0] = eh.NO_TEMP_MATCHED_DATA
                else:
                    try:
                        metrics = metrics_calculator(data=df_comb, gpi_info=date_info)
                    except Exception:
                        if handle_errors == "raise": raise
                        metrics = metrics_calculator(pd.DataFrame(columns=c_list), date_info)
                        metrics["status"][0] = eh.METRICS_CALCULATION_FAILED

                if metrics:
                    # Cleanup metrics dictionary
                    for k_pop in ["lat", "lon", "gpi"]:
                        metrics.pop(k_pop, None)
                    if isinstance(metrics["status"], (int, np.integer)):
                        metrics["status"] = np.array([metrics["status"]])
                    
                    metrics["date_time"] = time_np
                    res_list.append(metrics)

        except Exception as e:
            if handle_errors == 'raise':
                raise e
            elif handle_errors == "ignore":
                logging.error(f"{date_info}: {e}")
                result = val.dummy_validation_result(
                    date_info, rename_cols=False,
                    only_with_reference=only_with_reference)
                if isinstance(e, eh.ValidationError):
                    retcode = e.return_code
                else:
                    retcode = eh.VALIDATION_FAILED
                for key in result:
                    for k in result[key][0].keys():
                        # default case or subgroups status update
                        if (isinstance(k, str) and k == "status") or \
                            (isinstance(k, tuple) and k[1] == "status"):
                            result[key][0][k][0] = retcode  

        # 3. Efficiently merge into global results
        for r, metrics_data in result.items():
            results.setdefault(r, []).extend(metrics_data)

        # update progress every SAVE_INTERVAL timesteps or on the last timestep
        if validation_run is not None and (i % SAVE_INTERVAL == 0 or i == total_times - 1):
            validation_run.progress_spatial = max(1, round((i + 1) / total_times * 100))
            validation_run.save()
            
    c_results = compact_results(results)

    # Append the dictionary containing information about how often a GPI was used for calculation
    for key in gpi_n_use_dict.keys():
        c_results[key]["n_gpi_was_used"] = list(gpi_n_use_dict[key].values())
    # For meta-mapplots about gpi location
    for key in c_results.keys():
        c_results[key]["gpi"] = list(ds_use.gpi.values)
        c_results[key]["lat"] = list(ds_use.lat.values) 
        c_results[key]["lon"] = list(ds_use.lon.values)
    return c_results

def temporal_validation_xr(val, ds_use, only_with_reference=True, handle_errors="ignore", validation_run=None):
    """
    Performs a temporal validation using an xarray by calculating metrics for every gpi.

    Calculates metrics across time for a single GPI, this function 
    iterates through the 'gpi' dimension and calculates metrics across 
    all available timesteps (stations) for each gpi. 

    Parameters
    ----------
    val : ValidationRun
        The validation run object used for data retrieval and configuration.
    ds_use : xr.Dataset
        The consolidated dataset with dimensions ('date_time', 'gpi').
    only_with_reference: bool, optional (default: False)
        Only compute metrics for dataset combinations where the reference
        is included.

    Returns
    -------
    c_results : dict
        Compacted validation results containing the metrics for each 
        dataset combination, indexed by date_time.

    Raises
    ------
    eh.NoTempMatchedDataError
        If no data is found for a specific combination and error handling 
        is set to 'raise'.
    eh.MetricsCalculationError
        If the metrics calculator fails and error handling is set to 'raise'.

    """
    results = {}
    gpi_metakeys = [name for name, coord in ds_use.coords.items() if coord.dims == ('gpi',)]
    
    # 1. Pre-calculate combinations and structures outside the GPI loop
    all_combinations = {}
    for n, k in val.metrics_c:
        combos = list(get_result_combinations(val.data_manager.ds_dict, n=k))
        for c in combos:
            c_list = [j[0] for j in c]
            if only_with_reference and val.data_manager.reference_name not in c_list:
                continue
            all_combinations[c] = (c_list, val.metrics_c[(n, k)])

    # 2. Convert Dataset to DataFrame once (MultiIndex: gpi, date_time)
    # This is much faster than repeatedly calling .sel(gpi=gpi)
    df_all = ds_use.to_dataframe()
    
    # Pre-extract coordinate values for fast access
    lons = ds_use.lon.values
    lats = ds_use.lat.values
    gpi_vals = ds_use.gpi.values

    total_gpis = len(gpi_vals)
    SAVE_INTERVAL = max(1, total_gpis // 100)

    for i, gpi in enumerate(gpi_vals):
        try:
            result = {}
            # Faster slicing using the MultiIndex
            df_gpi = df_all.xs(gpi, level='gpi')
            
            gpi_meta = {key: ds_use[key].values[i] for key in gpi_metakeys} 
            gpi_info = (gpi, lons[i], lats[i], gpi_meta) 

            for c, (c_list, metrics_calculator) in all_combinations.items():
                res_list = result.setdefault(c, [])
                
                df_comb = df_gpi[c_list].dropna()
                
                if df_comb.empty:
                    if handle_errors == "raise":
                        raise eh.NoTempMatchedDataError(f"Empty data for {c} at {gpi_info}")
                    
                    metrics = metrics_calculator(pd.DataFrame(columns=c_list), gpi_info)
                    metrics["status"][0] = eh.NO_TEMP_MATCHED_DATA
                else:
                    try:
                        metrics_calculator.__self__.metadata_template = METADATA_TEMPLATE['ismn_ref']
                        metrics_calculator.__self__.result_template.update(metrics_calculator.__self__.metadata_template)
                        metrics = metrics_calculator(data=df_comb, gpi_info=gpi_info)
                    except Exception:
                        if handle_errors == "raise":
                            raise eh.MetricsCalculationError(f"Metrics failed for {c}")
                        metrics = metrics_calculator(pd.DataFrame(columns=c_list), gpi_info)
                        metrics["status"][0] = eh.METRICS_CALCULATION_FAILED
                
                res_list.append(metrics)
                
        except Exception as e:
            if handle_errors == 'raise':
                raise e
            elif handle_errors == "ignore":
                logging.error(f"{gpi_info}: {e}")
                result = val.dummy_validation_result(
                    gpi_info, rename_cols=False,
                    only_with_reference=only_with_reference)
                
                retcode = e.return_code if isinstance(e, eh.ValidationError) else eh.VALIDATION_FAILED
                
                for key in result:
                    for k in result[key][0].keys():
                        if (isinstance(k, str) and k == "status") or \
                           (isinstance(k, tuple) and k[1] == "status"):
                            result[key][0][k][0] = retcode  
        
        for r, metrics_data in result.items():
            results.setdefault(r, []).extend(metrics_data)

        if validation_run is not None and (i % SAVE_INTERVAL == 0 or i == total_gpis - 1):
            validation_run.progress = max(1, round((i + 1) / total_gpis * 100))
            validation_run.save()
            
    c_results = compact_results(results)
    return c_results

@shared_task(bind=True, max_retries=3)
def run_xArray_validation(self, validation_id, gpi_tuple, val_type="both", min_obs=1, include_secondary_meta=False, only_with_reference=ONLY_WITH_REFERENCE):
    """
    Executes a pytesmo-based validation using xArray datasets.

    The function builds an xArray from the provided GPIs, calculates 
    metadata coordinates (e.g., number of valid GPIs per timestamp), 
    filters by minimum observations, and performs spatial and/or 
    temporal validation.

    Parameters
    ----------
    validation_id : int
        Primary key of the ValidationRun object.
    gpi_tuple : tuple
        A tuple defining the Grid Point Indices (GPIs) to be processed.
    val_type : str, optional
        Type of validation to perform. Default is 'both'.
        'spatial' creates graphs for spatial validation.
        'spatial' creates graphs for spatial validation.
        'temporal' creates graphs for temporal validation.
        'both' performs both spatial and temporal validation.
    min_obs : int, optional
        Minimum number of valid samples (GPIs) required per timestamp 
        to include it in the validation. Default is 10.
    include_secondary_meta : bool, optional
        If True, calculates and adds secondary metadata dicts (land cover, 
        climate class, etc.). Default is False. NOT IMPLEMENTED
    only_with_reference : bool, optional
        Whether to restrict the validation to combinations with the reference 
        dataset.

    Return
    ------
    temporal_result : object or None
        Result of the temporal validation logic.
    spatial_result : object or None
        Result of the spatial validation logic.
    """
    numgpis = num_gpis_from_job(gpi_tuple)
    __logger.debug("Executing xArray validation for validation {}, # of gpis: {}".format(validation_id, numgpis))
    start_time = datetime.now(tzlocal())
    try:
        # Create Validation run
        validation_run = ValidationRun.objects.get(pk=validation_id)
        val = create_pytesmo_validation(validation_run, val_type="spatial")
        # Hijack run and create xArray
        ds_all = build_xarray(gpi_tuple, val)

        # create spatial metadata
        date_meta = {}
        first_var = next(iter(ds_all.data_vars))

        # secondary metadata not that useful
        if include_secondary_meta:
            metakeys = ["frm_class", "lc_2010", "climate_KG"] # for now only with classed values, no binning for continous meta implemented yet
            metalist = []
            for time in ds_all.date_time:
                mask = ds_all.sel(date_time=time)[first_var].values
                metadict = {key:pd.Series(np.where(np.isnan(mask), np.nan, ds_all.sel(date_time=time)[key].values)).value_counts(dropna=False).to_dict() for key in metakeys}
                metalist.append(metadict)

            for key in metakeys:
                ds_all.coords["n_gpi_"+key] = ("date_time", [metalist[time][key] for time in range(ds_all.date_time.__len__())])

        date_meta["n_gpi"] = ds_all[first_var].count(dim='gpi').values   
        ds_all.coords["n_gpi"] = ("date_time", date_meta["n_gpi"]) #Number of gpi where not all values are missing (at each timestamp)

        # Run validations depending on chosen type
        if val_type == "both":
            ds_use = ds_all.where(ds_all.n_gpi>=min_obs, drop=True) # if you want to filter beforehand: should be filtered to min_obs in pytesmo, probably 10
            if any(np.array([len(ds_use[coord]) for coord in ds_use.dims]) < 1):
                raise ValueError(f"No Timestamp with enough gpi observations")
            spatial_result = spatial_validation_xr(val, ds_use, only_with_reference, validation_run=validation_run)
            temporal_result = temporal_validation_xr(val, ds_all, only_with_reference, validation_run=validation_run)
            
        elif val_type == "spatial":
            ds_use = ds_all.where(ds_all.n_gpi>=min_obs, drop=True) # if you want to filter beforehand: should be filtered to min_obs in pytesmo, probably 10
            if any(np.array([len(ds_use[coord]) for coord in ds_use.dims]) < 1):
                raise ValueError(f"No Timestamp with enough gpi observations")
            spatial_result = spatial_validation_xr(val, ds_use, only_with_reference, validation_run=validation_run)
            temporal_result = None
        elif val_type == "temporal": #Shouldn't be used, original implementation way faster
            temporal_result = temporal_validation_xr(val, ds_use, only_with_reference, validation_run=validation_run)
            spatial_result = None
        else:
            spatial_result = None
            temporal_result = None

        end_time = datetime.now(tzlocal())
        duration = end_time - start_time
        duration = (duration.days * 86400) + duration.seconds
        __logger.debug(
            "Finished xArray validation for validation {}, took {} seconds for {} gpis".
            format(validation_id, duration, numgpis))
        return temporal_result, spatial_result
    except Exception as e:
        self.retry(countdown=2, exc=e)


def check_and_store_results(job_id, results, save_path):
    if len(results) < 1:
        __logger.warning(
            'Potentially problematic job: {} - no results'.format(job_id))
        return

    netcdf_results_manager(results, save_path)

def check_and_store_spatial_results(job_id, results, save_path):
    if len(results) < 1:
        __logger.warning(
            'Potentially problematic job: {} - no results'.format(job_id))
        return
    else:
        netcdf_results_manager_spatial(results, save_path)

def append_attributes_spatial(ds):
    """Appends certain attributes to dataset variables. Should be expanded."""
    for k in list(ds.keys()):
        if list(ds[k].coords.keys()) == ["date_time"]:
            ds[k].attrs["coordinates"] = "date_time"
        elif list(ds[k].coords.keys()) == ["gpi"]:
            ds[k].attrs["coordinates"] = "gpi"
        if k == "lon":
            ds[k].attrs = dict(
                        long_name="location longitude",
                        coordinates="gpi",
                        standard_name="longitude",
                        units="degrees_east",
                        valid_range=np.array([-180, 180]),
                        axis="X",
                    )
        if k == "lat":
            ds[k].attrs = dict(
                        long_name="location latitude",
                        coordinates="gpi",
                        standard_name="latitude",
                        units="degrees_north",
                        valid_range=np.array([-90, 90]),
                        axis="Y",
                    )
    return ds
    
def netcdf_results_manager_spatial(results, run_dir):
    for ds_names, data in results.items():
        fname = build_filename(run_dir, ds_names)

        meta = {k:v for k, v in data.items() if len(v) == len(data["gpi"])}
        data = {k:v for k, v in data.items() if len(v) != len(data["gpi"])}
        ds = xr.Dataset()
        for key, values in data.items():
            # Create a coordinate for the values (e.g., obs_index)
            # and a coordinate for the key itself
            ds[key] = xr.DataArray(
                values, 
                dims=["date_time"])

        for m_key, m_val in meta.items():
            # If meta is a complex dict, JSON serialize it
            if isinstance(m_val, dict):
                ds[m_key] = xr.DataArray(json.dumps(m_val), dims=["gpi"],coords={"gpi": meta["gpi"]})
            else:
                ds[m_key] = xr.DataArray(m_val, dims=["gpi"],coords={"gpi": meta["gpi"]})
        ds = append_attributes_spatial(ds)
        ds.to_netcdf(fname.replace(".nc", ".SPATIAL.nc"))

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


def run_validation(validation_id, val_type="temporal"):

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
        if val_type=="temporal":
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
        elif val_type in ["both", "spatial"]:
            total_points, jobs = create_jobs(
                validation_run=validation_run,
                reader=ref_reader,
                dataset_config=validation_run.spatial_reference_configuration)
            jobs = [tuple([i for i in np.concatenate(jobs, axis=1)])] # Only run one big job, otherwise parallelization makes xArray creation impossible
            validation_run.total_points = total_points
            validation_run.save()  # save the number of gpis before we start

            __logger.debug("Jobs to run: {}".format([job[:-1] for job in jobs]))

            save_path = run_dir

            async_results = []
            job_table = {}
            for j in jobs:
                celery_job = run_xArray_validation.apply_async(
                    args=[validation_id, j, val_type], queue=validation_run.user.username)
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
                    
                    if val_type=="temporal":
                        results = _pytesmo_to_qa4sm_results(results)
                        check_and_store_results(async_result.id, results, run_dir)
                    elif val_type in ["both", "spatial"]:
                        temporal_result, spatial_result = results
                        sr = _pytesmo_to_qa4sm_results(spatial_result)
                        check_and_store_spatial_results(async_result.id, sr, run_dir)
                        if val_type=="both":
                            tr = _pytesmo_to_qa4sm_results(temporal_result)
                            results = tr
                            check_and_store_results(async_result.id, results, run_dir)

                    # If the job ran successfully, we have to check the status
                    # attribute to see if the job actually calculated something
                    # (ok) or had an error.
                    # In principle we might have different result status for
                    # different dataset combinations, because it might happen
                    # that in one case the validation fails because there is
                    # not enough data. For "ok_points" we only count the points
                    # where all validations fail.
                    def get_ok_points(result):
                        """Iterates over status keys in dataset to determine # of gpi/date_time where every calculation worked"""
                        result_key = list(result.keys())[0]  # there is only 1 key
                        res = result[result_key]
                        status_result_keys = list(
                            filter(
                                lambda s: "status" in s and not s.split("|")[0].
                                isdigit(), res.keys()))
                        ok = res[status_result_keys[0]] == 0
                        for statkey in status_result_keys[1:]:
                            ok = ok & (res[statkey] == 0)
                        nok = sum(ok)
                        return nok, ok
                    
                    validation_run.ok_times = 0
                    validation_run.error_times = 0

                    if val_type in ["both", "temporal"]:
                        nok, ok = get_ok_points(results)                     
                        ngpis = num_gpis_from_job(
                            job_table[async_result.id]
                        )  # ? so we need a new criterion to determine, if the job was ok or not? like ngpis * len(time slices)
                        validation_run.ok_points += nok
                        validation_run.error_points += ngpis - nok

                        if val_type == "both":
                            nok, ok = get_ok_points(sr)                     
                            ntimes = len(sr[list(sr.keys())[0]]["date_time"])
                            validation_run.ok_times += nok
                            validation_run.error_times += ntimes - nok
                            validation_run.total_times = ntimes

                    elif val_type == "spatial":
                        nok, ok = get_ok_points(sr)                     
                        ntimes = len(sr[list(sr.keys())[0]]["date_time"])
                        validation_run.ok_times += nok
                        validation_run.error_times += ntimes - nok
                        validation_run.total_times = ntimes

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
                
                if val_type == "temporal":
                    validation_run.progress = round(
                        (validation_run.ok_points + validation_run.error_points) /
                        validation_run.total_points * 100)
                  
                elif val_type == "spatial":
                    validation_run.progress_spatial = round(
                        (validation_run.ok_times + validation_run.error_times) /
                        validation_run.total_times * 100)
                    validation_run.progress = validation_run.progress_spatial 

                elif val_type == "both":
                    validation_run.refresh_from_db(fields=['progress', 'progress_spatial'])
                    pass
                      
            else:
                validation_run.progress = -1
                validation_run.progress_spatial = -1

            validation_run.save()
            __logger.info(
                "Dealt with task {}, validation {} is {} % done...".format(
                    async_result.id, validation_run.id,
                    validation_run.progress))

        # once all tasks are finished:
        # only store parameters and produce graphs if validation wasn't cancelled and
        # we have metrics for at least one gpi - otherwise no netcdf output file

        if (not validation_aborted):
            if val_type in ["spatial", "both"]:
                set_outfile(validation_run, run_dir, val_type="spatial") 

                iam_dict = define_tsw_metrics(validation_run,
                            get_period(validation_run))
                temp_sub_wdw_instance = iam_dict['temp_sub_wdw_instance']
                temp_sub_wdws = iam_dict['temp_sub_wdws']

                sp_transcriber = Pytesmo2Qa4smResultsTranscriber(
                    pytesmo_results=os.path.join(OUTPUT_FOLDER,
                                                validation_run.output_file_spatial.name),
                                                intra_annual_slices=temp_sub_wdw_instance,
                                                keep_pytesmo_ncfile=False)
                if sp_transcriber.exists:
                    restructured_results = sp_transcriber.get_transcribed_dataset()


                    base = os.path.basename(validation_run.output_file_spatial.name).replace('.SPATIAL.nc', '_spatial_result.nc')
                    spatial_outname = os.path.join(run_dir, base)
                    
                    restructured_results.to_netcdf(spatial_outname)
                    
                    # Update DB reference
                    validation_run.output_file_spatial.name = regex_sub(
                        '/?' + OUTPUT_FOLDER + '/?', '', spatial_outname)
                    validation_run.save()

                    # Copy attributes from temporal file to spatial file
                    # Add required attributes directly
                    with netCDF4.Dataset(spatial_outname, 'a') as ds:
                        ds.val_ref = 'val_dc_dataset0'
                        j = 1
                        for dataset_config in validation_run.dataset_configurations.all():
                            if (validation_run.spatial_reference_configuration and
                                    dataset_config.id == validation_run.spatial_reference_configuration.id):
                                i = 0
                            else:
                                i = j
                                j += 1
                            ds.setncattr('val_dc_dataset' + str(i), dataset_config.dataset.short_name)
                            ds.setncattr('val_dc_version' + str(i), dataset_config.version.short_name)
                            ds.setncattr('val_dc_variable' + str(i), dataset_config.variable.pretty_name)
                            ds.setncattr('val_dc_dataset_pretty_name' + str(i), dataset_config.dataset.pretty_name)
                            ds.setncattr('val_dc_version_pretty_name' + str(i), dataset_config.version.pretty_name)
                            ds.setncattr('val_dc_variable_pretty_name' + str(i), dataset_config.variable.short_name)
                        ds.val_scaling_method = validation_run.scaling_method
                        ds.val_anomalies = validation_run.anomalies
                   
                    sp_transcriber.compress(path=spatial_outname, compression='zlib', complevel=9)

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
                        save_metadata=validation_run.plots_save_metadata,
                        val_type="spatial")

            if val_type in ["temporal", "both"]:
                set_outfile(validation_run, run_dir, val_type="temporal")

                iam_dict = define_tsw_metrics(validation_run,
                                            get_period(validation_run))
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
                        save_metadata=validation_run.plots_save_metadata,
                        val_type="temporal")

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
    validation_run.progress_spatial = -1
    validation_run.save()

    celery_tasks = CeleryTask.objects.filter(validation=validation_run)

    for task in celery_tasks:
        app.control.revoke(str(task.celery_task_id))  # @UndefinedVariable
        task.delete()

    run_dir = os.path.join(OUTPUT_FOLDER, str(validation_run.id))
    if os.path.exists(run_dir):
        __logger.info(
            'Validation got cancelled, so the result files should be cleaned.')
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
            statics = ["gpi", "lat", "lon", "date_time"] # had to append date_time to avoid rewriting entire function
            statics.extend(METADATA_TEMPLATE["ismn_ref"])
            if metric in statics:
                new_key = metric
            else:
                datasets = list(map(lambda t: t[0], key))
                if metric[0] == '(' and metric[-1] == ')':
                    metric = ast.literal_eval(
                        metric
                    )  # casts the string representing a tuple to a real tuple
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
        startdate = val_run.interval_from.astimezone(UTC).replace(tzinfo=None)
        enddate = val_run.interval_to.astimezone(UTC).replace(tzinfo=None)
        return [startdate, enddate]
    return None


def define_tsw_metrics(
    val_run: ValidationRun, period: List
) -> Dict[str, Union[TemporalSubWindowsCreator, Dict[str, TsDistributor],
                     None]]:
    '''
    Extract the temporal sub-window metrics settings from the validation run and instantiate the corresponding objects.

    Parameters
    ----------
    val_run : ValidationRun
        The validation run object
    period : List
        The period of a validation run

    Returns
    -------
    Dict[str, Union[TemporalSubWindowsCreator, Dict[str, TsDistributor], None]]
        A dictionary containing the temporal sub-window instance and the custom temporal sub-windows, if applicable. Otherwise, filled with None.
    '''
    temp_sub_wdw_instance = None

    # Handle intra-annual metrics
    if val_run.intra_annual_metrics:
        intra_annual_metric_lut = {
            'Seasonal': 'seasons',
            'Monthly': 'months'
        }  # TODO implement properly in qa4sm_reader.globals
        temp_sub_wdw_instance = TemporalSubWindowsFactory.create(
            temporal_sub_window_type=intra_annual_metric_lut[
                val_run.intra_annual_type],
            overlap=int(val_run.intra_annual_overlap),
            period=period)

    # Handle stability metrics
    elif val_run.stability_metrics:
        temp_sub_wdw_instance = TemporalSubWindowsFactory.create(
            temporal_sub_window_type="stability",
            overlap=0,  # Adjust overlap for stability metrics
            period=period,
            custom_subwindows=TEMPORAL_SUB_WINDOWS.get('custom', None))

    temp_sub_wdws = temp_sub_wdw_instance.custom_temporal_sub_windows if temp_sub_wdw_instance else None

    __logger.debug(f"{temp_sub_wdw_instance=}")
    __logger.debug(f"{temp_sub_wdws=}")
    return {
        'temp_sub_wdw_instance': temp_sub_wdw_instance,
        'temp_sub_wdws': temp_sub_wdws
    }
