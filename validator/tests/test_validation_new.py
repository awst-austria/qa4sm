## this file is an updated version of the test_validation.py file, but adapted to be more flexible

import errno
import fnmatch
import logging
import os
import shutil
import time
from datetime import datetime
from os import path
from re import IGNORECASE  # @UnresolvedImport
from re import search as regex_search
from re import match as regex_match
from zipfile import ZipFile
from typing import Dict, Union, List, Tuple, Callable, Any
from pathlib import Path

from netCDF4 import Dataset as ncDataset
import numpy as np
import pandas as pd
import pytest
from dateutil.tz import tzlocal
from django.contrib.auth import get_user_model
from api.tests import test_validation_config_view

from api.views import auxiliary_functions
from validator.validation.validation import compare_validation_runs, copy_validationrun
from validator.tests.auxiliary_functions import generate_ismn_upscaling_validation
# from validator.tests.auxiliary_functions_new import generate_ismn_upscaling_validation
import validator.tests.auxiliary_functions_new as aux
from django.test import TestCase
from django.test.utils import override_settings
from pytz import UTC

from django.conf import settings
from validator.models import DataFilter
from validator.models import DataVariable
from validator.models import Dataset
from validator.models import DatasetConfiguration
from validator.models import DatasetVersion
from validator.models import ParametrisedFilter
from validator.models import ValidationRun
from validator.models import CopiedValidations
from validator.tests.testutils import set_dataset_paths
from validator.validation import globals, adapt_timestamp
import validator.validation as val
from validator.validation.batches import _geographic_subsetting, create_upscaling_lut
from validator.validation.globals import DEFAULT_TSW, METRICS, TC_METRICS, METADATA_PLOT_NAMES, NON_METRICS, OVERLAP_MIN, OVERLAP_MAX, OUTPUT_FOLDER
from validator.validation.util import get_function_name
from validator.tests.valruns_for_tests import TestValidationRunType, validations_runs_lut, tcol_validations_runs_lut, ismn_upscaling_validations_runs_lut
from django.shortcuts import get_object_or_404
from math import comb

from qa4sm_reader.globals import out_metadata_plots, _metadata_exclude, CLUSTERED_BOX_PLOT_SAVENAME
from qa4sm_reader.utils import transcribe

User = get_user_model()


@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestValidation(TestCase):
    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']
    hawaii_coordinates = [18.16464, -158.79638, 22.21588, -155.06103]

    __logger = logging.getLogger(__name__)

    def get_test_validation_run(self, run_type):
        """ Unified method to access validation run dictionaries based on run_type """
        if run_type == 'default':
            return validations_runs_lut
        elif run_type == 'tcol':
            return tcol_validations_runs_lut
        elif run_type == 'ismn_upscaling':
            return ismn_upscaling_validations_runs_lut
        else:
            raise ValueError(f"Unknown validation run type: {run_type}")

    def setUp(self):
        self.metrics = ['gpi', 'lon', 'lat'] + list(METRICS.keys())
        self.tcol_metrics = list(TC_METRICS.keys())

        self.user_data = {
            'username': 'testuser',
            'password': 'secret',
            'email': 'noreply@awst.at'
        }
        self.user2_data = {
            'username': 'bojack',
            'password': 'horseman',
            'email': 'bojack@awst.at'
        }

        try:
            self.testuser = User.objects.get(
                username=self.user_data['username'])
            self.testuser2 = User.objects.get(
                username=self.user2_data['username'])
        except User.DoesNotExist:
            self.testuser = User.objects.create_user(**self.user_data)
            self.testuser2 = User.objects.create_user(**self.user2_data)

        try:
            os.makedirs(val.OUTPUT_FOLDER)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        set_dataset_paths()

    # check output of validation

    def _check_validation_configuration_consistency(
            self, validation: ValidationRun,
            expected_results: Dict[str, Union[str, float, int, None]]) -> None:
        """
        Checks if validation configuration is proper, i.e. if the scaling, temporal and spatial reference configurations,
        assigned to the particular validation have proper fields set to True, if not throws an error

        This function is used to verify if our validation test cases are properly written. After the change in
        the way we treat reference, there were some changes to the validation and data_configuration models and now tests
        have to be consistent with those changes.

        The function is not used in the API tests, as there we do not verify a saved validation, but parameters coming
        from the frontend, so there are slightly different conditions to check.

        Parameters
        ----------
        validation: ValidationRun instance

        Returns
        -------
        """
        val_configs = DatasetConfiguration.objects.filter(
            validation=validation)
        scaling_ref = validation.scaling_ref

        # check if there is no scaling reference set if the method is none
        if validation.scaling_method == 'none':
            if scaling_ref:
                if scaling_ref.is_scaling_reference or len(
                        val_configs.filter(is_scaling_reference=True)) != 0:
                    raise ValueError(
                        'Scaling method is none, but scaling reference is set and a configuration is '
                        'marked as reference.')
                raise ValueError(
                    'Scaling method is none, but scaling reference is set.')
            else:
                if len(val_configs.filter(is_scaling_reference=True)) != 0:
                    raise ValueError(
                        'Scaling method is not set but at least one configuration is marked as reference.'
                    )
        else:
            if scaling_ref:
                if len(val_configs.filter(is_scaling_reference=True)) == 0:
                    raise ValueError(
                        'No configuration is marked as scaling reference.')
                elif len(val_configs.filter(is_scaling_reference=True)) > 1:
                    raise ValueError(
                        'More than one configuration is marked as scaling reference.'
                    )
                if not scaling_ref.is_scaling_reference:
                    raise ValueError(
                        'Configuration is not marked as scaling reference.')
            else:
                raise ValueError(
                    'Scaling method is set, but scaling reference not.')

        # check if only one configuration has proper field set:
        if len(val_configs.filter(is_spatial_reference=True)) == 0:
            raise ValueError(
                'No configuration is marked as spatial reference.')
        elif len(val_configs.filter(is_spatial_reference=True)) > 1:
            raise ValueError(
                'More than one configuration is marked as spatial reference.')

        if len(val_configs.filter(is_temporal_reference=True)) == 0:
            raise ValueError(
                'No configuration is marked as temporal reference.')
        elif len(val_configs.filter(is_temporal_reference=True)) > 1:
            raise ValueError(
                'More than one configuration is marked as temporal reference.')

        # check if proper reference configurations have proper fields set
        if not validation.spatial_reference_configuration.is_spatial_reference:
            raise ValueError(
                'Configuration is not marked as spatial reference.')
        if not validation.temporal_reference_configuration.is_temporal_reference:
            raise ValueError(
                'Configuration is not marked as temporal reference.')

        # check for intra-annual metrics
        if validation.intra_annual_metrics != expected_results[
                'intra_annual_metrics']:
            raise ValueError(
                f'Intra-annual metrics are not configured properly. Expected "{expected_results["intra_annual_metrics"]}", but got "{validation.intra_annual_metrics=}".'
            )

        if validation.intra_annual_type != expected_results[
                'intra_annual_type']:
            raise ValueError(
                f'Intra-annual type is not configured properly. Expected "{expected_results["intra_annual_type"]}", but got "{validation.intra_annual_type=}".'
            )

        if validation.intra_annual_overlap != expected_results[
                'intra_annual_overlap']:
            raise ValueError(
                f'Intra-annual overlap is not configured properly. Expected "{expected_results["intra_annual_overlap"]}", but got "{validation.intra_annual_overlap=}".'
            )

        # above the expected results are verified against the actual results
        # below though, we check if the expected results (which we now know are identical with the actua results) are consistent with what in general makes sense
        # the purpose is to make sure that the results are not nonsense and follow their respective rules
        # e.g. just because we expect an overlap of -1 and the actual overlap is -1, doesn't mean that this is a valid configuration

        # this is the default case, check default values
        if expected_results['intra_annual_metrics'] == False:
            if validation.intra_annual_overlap != 0:
                raise ValueError(
                    f'The default intra-annual overlap should be 0, but is found to be {validation.intra_annual_overlap=}.'
                )

            if validation.intra_annual_type != None:
                raise ValueError(
                    f'The default intra-annual type should be "None", but is found to be {validation.intra_annual_type=}.'
                )

        elif expected_results['intra_annual_metrics'] == True:
            if validation.intra_annual_overlap < OVERLAP_MIN:
                raise ValueError(
                    f'The intra-annual overlap should not be below 0, as this does not make sense. Yet, it is found to be {validation.intra_annual_overlap=}.'
                )

            elif validation.intra_annual_overlap > OVERLAP_MAX:
                raise ValueError(
                    f'The intra-annual overlap should not be above {OVERLAP_MAX}, bit is found to be {validation.intra_annual_overlap=}.'
                )

            elif validation.intra_annual_overlap != expected_results[
                    'intra_annual_overlap']:
                raise ValueError(
                    f'The intra-annual overlap should be {expected_results["intra_annual_overlap"]}, but is found to be {validation.intra_annual_overlap=}.'
                )

            if validation.intra_annual_type not in ['Seasonal', 'Monthly']:
                raise ValueError(
                    f'If intra annual metrics are to be calculated, this is to be done either on a monthly or seasonal basis. Thus, allowed values are ["Seasonal", "Monthly"], not {validation.intra_annual_type=}.'
                )

    def check_results(
        self,
        run,
        is_tcol_run=False,
        meta_plots=True,
        expected_results: Dict[str, Any] = {
            'intra_annual_metrics': False,
            'intra_annual_type': None,
            'intra_annual_overlap': 0
        }):

        try:
            self._check_validation_configuration_consistency(
                run, expected_results)
        except Exception as exc:
            assert False, f"'_check_validation_configuration raised and exception {exc}'"

        assert run is not None
        assert run.end_time is not None
        assert run.end_time > run.start_time
        assert run.total_points > 0
        assert run.error_points >= 0
        assert run.ok_points >= 0

        assert run.output_file

        outdir = os.path.dirname(run.output_file.path)

        n_datasets = run.dataset_configurations.count()

        tcol_metrics = self.tcol_metrics if is_tcol_run else []
        non_metrics = ['gpi', 'lon', 'lat']
        comm_metrics = ['n_obs', 'status']
        pair_metrics = [
            m for m in list(METRICS.keys()) if m.lower() not in comm_metrics
        ]

        # check netcdf output
        length = -1
        num_vars = -1
        with ncDataset(run.output_file.path, mode='r') as ds:
            assert ds.qa4sm_version == settings.APP_VERSION
            assert ds.qa4sm_env_url == settings.ENV_FILE_URL_TEMPLATE.format(
                settings.APP_VERSION)
            assert str(run.id) in ds.url
            assert settings.SITE_URL in ds.url

            # check the metrics contained in the file
            for metric in self.metrics + tcol_metrics:  # we dont test lon, lat, time etc.
                ## This gets all variables in the netcdf file that start with the name of the current metric
                if metric in tcol_metrics:
                    metric_vars = ds.get_variables_by_attributes(
                        name=lambda v: regex_search(
                            r'^{}(.+?_between|$)'.format(metric), v, IGNORECASE
                        ) is not None)

                    # since metric vars for the reference dataset are written to the file, we have to filter them out
                    # essentially filters such metric vars out: {METRIC}_{DATASET_A}_between_{DATASET_A}_and_{WHATEVER}
                    #TODO: this is a bit of a hack, we should find a better way to do handle these specific cases

                    self_combination_pattern = r'^(.*?_)([^_]+)(_between_\2_and_.*)$'
                    metric_vars = [
                        tcmetric_var
                        for tcmetric_var in metric_vars if not regex_match(
                            self_combination_pattern, tcmetric_var.name)
                    ]

                else:
                    metric_vars = ds.get_variables_by_attributes(
                        name=lambda v: regex_search(
                            r'^{}(_between|$)'.format(metric), v, IGNORECASE
                        ) is not None)

                self.__logger.debug(
                    f'Metric variables for metric {metric} are {[m.name for m in metric_vars]}'
                )

                # check that all metrics have the same number of variables (depends on number of input datasets)
                if metric == 'status':
                    # for status we generate 1 plot for non-spatial-reference dataset and one for each tcol combination
                    num_vars = (n_datasets -
                                1) + is_tcol_run * comb(n_datasets - 1, 2)
                elif (metric in comm_metrics) or (metric in non_metrics):
                    num_vars = 1
                elif metric in pair_metrics:
                    num_vars = n_datasets - 1
                elif metric in tcol_metrics:
                    # for this testcase CIs via bootstrapping are activated, so
                    # for every metric there's the value and lower and upper CI
                    # values.
                    num_vars = (n_datasets - 1) * 3
                else:
                    raise ValueError(f"Unknown metric {metric}")

                assert len(metric_vars
                           ) > 0, 'No variables containing metric {}'.format(
                               metric)
                assert len(
                    metric_vars
                ) == num_vars, 'Number of variables for metric {} doesn\'t match number for other metrics'.format(
                    metric)

                # check the values of the variables for formal criteria (not empty, matches lenght of other variables, doesn't have too many NaNs)
                for m_var in metric_vars:
                    self.__logger.debug(f"\nChecking variable {m_var.name}")
                    values = m_var[:]
                    assert values is not None

                    if length == -1:
                        length = len(values)
                        assert length > 0, 'Variable {} has no entries'.format(
                            m_var.name)
                    else:
                        assert len(
                            values
                        ) == length, 'Variable q{} doesn\'t match other variables in length'.format(
                            m_var.name)
                    self.__logger.debug(f'Length {m_var.name} are {length}')

                    # NaNs should only occur if the validation failed somehow
                    nan_ratio = np.sum(np.isnan(values.data)) / float(
                        len(values))
                    error_ratio = run.error_points / run.total_points
                    assert nan_ratio <= error_ratio, 'Variable {} has too many NaNs. Ratio: {}'.format(
                        metric, nan_ratio)

            if run.interval_from is None:
                assert ds.val_interval_from == "N/A", 'Wrong validation config attribute. [interval_from]'
            else:
                assert ds.val_interval_from == run.interval_from.strftime(
                    '%Y-%m-%d %H:%M'
                ), 'Wrong validation config attribute. [interval_from]'

            if run.interval_to is None:
                assert ds.val_interval_to == "N/A", 'Wrong validation config attribute. [interval_to]'
            else:
                assert ds.val_interval_to == run.interval_to.strftime(
                    '%Y-%m-%d %H:%M'
                ), 'Wrong validation config attribute. [interval_to]'

            assert run.anomalies == ds.val_anomalies, 'Wrong validation config attribute. [anomalies]'
            if run.anomalies == ValidationRun.CLIMATOLOGY:
                assert ds.val_anomalies_from == run.anomalies_from.strftime(
                    '%Y-%m-%d %H:%M'), 'Anomalies baseline start wrong'
                assert ds.val_anomalies_to == run.anomalies_to.strftime(
                    '%Y-%m-%d %H:%M'), 'Anomalies baseline end wrong'
            else:
                assert 'val_anomalies_from' not in ds.ncattrs(
                ), 'Anomalies baseline period start should not be set'
                assert 'val_anomalies_to' not in ds.ncattrs(
                ), 'Anomalies baseline period end should not be set'

            if all(x is not None for x in
                   [run.min_lat, run.min_lon, run.max_lat, run.max_lon]):
                assert ds.val_spatial_subset == "[{}, {}, {}, {}]".format(
                    run.min_lat, run.min_lon, run.max_lat, run.max_lon)

            i = 0
            for dataset_config in run.dataset_configurations.all():

                if (run.spatial_reference_configuration
                        and (dataset_config.id
                             == run.spatial_reference_configuration.id)):
                    d_index = 0
                else:
                    i += 1
                    d_index = i

                ds_name = 'val_dc_dataset' + str(d_index)
                stored_dataset = ds.getncattr(ds_name)
                stored_version = ds.getncattr('val_dc_version' + str(d_index))
                stored_variable = ds.getncattr('val_dc_variable' +
                                               str(d_index))
                stored_filters = ds.getncattr('val_dc_filters' + str(d_index))

                stored_dataset_pretty = ds.getncattr(
                    'val_dc_dataset_pretty_name' + str(d_index))
                stored_version_pretty = ds.getncattr(
                    'val_dc_version_pretty_name' + str(d_index))
                stored_variable_pretty = ds.getncattr(
                    'val_dc_variable_pretty_name' + str(d_index))

                # check dataset, version, variable
                assert stored_dataset == dataset_config.dataset.short_name, 'Wrong dataset config attribute. [dataset]'
                assert stored_version == dataset_config.version.short_name, 'Wrong dataset config attribute. [version]'
                assert stored_variable == dataset_config.variable.pretty_name, 'Wrong dataset config attribute. [variable]'

                assert stored_dataset_pretty == dataset_config.dataset.pretty_name, 'Wrong dataset config attribute. [dataset pretty name]'
                assert stored_version_pretty == dataset_config.version.pretty_name, 'Wrong dataset config attribute. [version pretty name]'
                assert stored_variable_pretty == dataset_config.variable.short_name, 'Wrong dataset config attribute. [variable pretty name]'

                # check filters
                if not dataset_config.filters.all(
                ) and not dataset_config.parametrisedfilter_set.all():
                    assert stored_filters == 'N/A', 'Wrong dataset config filters (should be none)'
                else:
                    assert stored_filters, 'Wrong dataset config filters (shouldn\'t be empty)'
                    for fil in dataset_config.filters.all():
                        assert fil.description in stored_filters, 'Wrong dataset config filters'
                    for pfil in dataset_config.parametrisedfilter_set.all():
                        assert pfil.filter.description in stored_filters, 'Wrong dataset config parametrised filters'
                        assert pfil.parameters in stored_filters, 'Wrong dataset config parametrised filters: no parameters'

                # check reference
                if dataset_config.id == run.spatial_reference_configuration.id:
                    assert ds.val_ref == ds_name, 'Wrong validation config attribute. [spatial_reference_configuration]'

                    if run.spatial_reference_configuration.dataset.short_name != "ISMN":
                        assert ds.val_resolution == run.spatial_reference_configuration.dataset.resolution[
                            "value"]
                        assert ds.val_resolution_unit == run.spatial_reference_configuration.dataset.resolution[
                            "unit"]

                if run.scaling_ref and dataset_config.id == run.scaling_ref.id:
                    assert ds.val_scaling_ref == ds_name, 'Wrong validation config attribute. [scaling_ref]'

            assert ds.val_scaling_method == run.scaling_method, ' Wrong validation config attribute. [scaling_method]'

        #----------------------check output files and dirs-----------------------
        #check if the output directory exists
        assert os.path.exists(outdir)

        # check files and dirs present in the output directory
        # there should always be 1x netcdf file, 1x graphs.zip, 1x statistics.zip & at least one additional directory called 'bulk'

        files_dirs_tbe = {
            'dirs': [globals.DEFAULT_TSW],
            'zips': ['graphs.zip', 'statistics.zip'],
        }

        # zip archives
        if run.intra_annual_metrics:
            files_dirs_tbe['dirs_in_stats_zip'] = [
                x for x in files_dirs_tbe['dirs']
            ]  # create new list to avoid reference

            if run.intra_annual_type == 'Seasonal':
                files_dirs_tbe['dirs_in_stats_zip'].extend(
                    list(globals.TEMPORAL_SUB_WINDOWS['seasons'].keys()))
            elif run.intra_annual_type == 'Monthly':
                files_dirs_tbe['dirs_in_stats_zip'].extend(
                    list(globals.TEMPORAL_SUB_WINDOWS['months'].keys()))

            files_dirs_tbe['dirs_in_graphs_zip'] = [
                x for x in files_dirs_tbe['dirs_in_stats_zip']
            ]  # create new list to avoid reference
            files_dirs_tbe['dirs_in_graphs_zip'].append('comparison_boxplots')

            files_dirs_tbe['dirs'].append('comparison_boxplots')

            #-----------------------------------------check comparison boxplots-----------------------------------------
            comparison_boxplots = [
                CLUSTERED_BOX_PLOT_SAVENAME.format(metric=x, filetype='png')
                for x in METRICS if x not in _metadata_exclude and x != 'n_obs'
            ]
            assert set(os.listdir(os.path.join(
                outdir, 'comparison_boxplots'))) == set(comparison_boxplots)

        def test_zips(zip_pth: str, dirs_tbe: List[str]):
            assert os.path.isfile(zip_pth)

            with ZipFile(zip_pth, 'r') as myzip:
                assert myzip.testzip(
                ) is None  # check if the zip file is not corrupted

                directories = {
                    str(Path(info.filename).parent)
                    for info in myzip.infolist()
                }
                if directories == set(
                        '.'):  # happens when no directories are present
                    directories = set()
                assert directories == set(dirs_tbe)

        for z in files_dirs_tbe['zips']:
            if 'statistics' in z:
                try:
                    expected_dirs = files_dirs_tbe['dirs_in_stats_zip']
                except KeyError:  # bulk case, only 'bulk' in statistics.zip
                    expected_dirs = [DEFAULT_TSW]
            elif 'graphs' in z:
                try:
                    expected_dirs = files_dirs_tbe['dirs_in_graphs_zip']
                except KeyError:  # bulk case, no dirs in graphs.zip
                    expected_dirs = []

            test_zips(os.path.join(outdir, z), expected_dirs)

            #-------------------------------------------check stats csv files-------------------------------------------
            if 'statistics' in z:
                with ZipFile(os.path.join(outdir, z), 'r') as myzip:
                    zipped_csvs = set([
                        info.filename for info in myzip.infolist()
                        if info.filename.endswith('.csv')
                    ])
                    expected_csvs = set([
                        os.path.join(d, f'{d}_statistics_table.csv')
                        for d in expected_dirs
                    ])

                assert zipped_csvs == expected_csvs

        #dirs present
        assert {
            x
            for x in os.listdir(outdir)
            if os.path.isdir(os.path.join(outdir, x))
        } == set(files_dirs_tbe['dirs'])

        #-------------------------------------------check all output graphics-------------------------------------------
        for metric in pair_metrics + comm_metrics + tcol_metrics:
            """
            For each pairwise metric: - n-1 overview maps (not for spat. ref.)
                                      - 1 boxplot
                                      - 4 metadata boxplots (not for pvalues)
            For each tcol metric: - n-1 overview maps
                                  - n-1 boxplots
                                  - 4 metadata boxplots
            For status: - 1 overview map
            """
            if metric in ['status']:
                continue

            if metric in tcol_metrics:
                n_metric_plots = (n_datasets - 1)
            elif metric in pair_metrics + comm_metrics:
                n_metric_plots = 1
            else:
                raise ValueError(f'Unknown metric: {metric}')

            if (metric in ['p_R', 'p_rho']) or (meta_plots is False):
                n_metadata_plots = 0
            else:
                n_metadata_plots = len(out_metadata_plots)

            # bulk graphics in .png format
            bulk_png_graphics = [os.path.join(f"{globals.DEFAULT_TSW}_boxplot_{metric}_metadata_{'_and_'.join(meta_var)}.png")
                        for meta_var in out_metadata_plots.values()] + \
                       [f'{globals.DEFAULT_TSW}_boxplot_{metric}.png', f'{globals.DEFAULT_TSW}_boxplot_{metric}_for_*.png']
            self.__logger.debug(f"{bulk_png_graphics=}")
            # bulk graphics in .svg format
            bulk_svg_graphics = [
                x.replace('.png', '.svg') for x in bulk_png_graphics
            ]  #TODO

            # graphics for temporal sub-windows
            if run.intra_annual_metrics:
                tsws = [
                    x for x in files_dirs_tbe['dirs_in_graphs_zip']
                    if x != 'comparison_boxplots' and x != DEFAULT_TSW
                ]
                tsw_png_graphics = [
                    os.path.join(tsw, f'{tsw}_boxplot_{metric}.png')
                    for tsw in tsws
                ]
                tsw_svg_graphics = [
                    x.replace('.png', '.svg') for x in tsw_png_graphics
                ]

                self.__logger.debug(f"{tsw_png_graphics=}")
                with ZipFile(os.path.join(outdir, 'graphs.zip'), 'r') as myzip:
                    zipped_graphics = set([
                        info.filename for info in myzip.infolist()
                        if info.filename.endswith('.png')
                        or info.filename.endswith('.svg')
                    ])
                    expected_graphics = set(tsw_png_graphics +
                                            tsw_svg_graphics)

                    for graphic in expected_graphics:
                        assert graphic in zipped_graphics

            # check for png bulk graphics in outdir
            boxplot_pngs = [
                x
                for x in os.listdir(os.path.join(outdir, globals.DEFAULT_TSW))
                if any([fnmatch.fnmatch(x, p) for p in bulk_png_graphics])
            ]
            self.__logger.debug(f"{boxplot_pngs=}")
            self.__logger.debug(
                f"{metric}: Plots are {len(boxplot_pngs)}, "
                f"should: {n_metadata_plots} + {n_metric_plots}")

            assert len(boxplot_pngs) == n_metadata_plots + n_metric_plots

            overview_pngs = [
                x
                for x in os.listdir(os.path.join(outdir, globals.DEFAULT_TSW))
                if fnmatch.fnmatch(
                    x, f'{globals.DEFAULT_TSW}_overview*_{metric}.png')
            ]

            self.__logger.debug(f"{overview_pngs=}")
            self.__logger.debug(f"{metric}: Plots are {len(overview_pngs)}, "
                                f"should: {(n_datasets - 1)}")

        #---------------------------------------------check tsw status plots---------------------------------------------
        if run.intra_annual_metrics:
            tsw_status_graphics_png = [
                os.path.join(tsw, f'{tsw}_barplot_status.png') for tsw in tsws
            ]
            tsw_status_graphics_svg = [
                x.replace('.png', '.svg') for x in tsw_status_graphics_png
            ]

            with ZipFile(os.path.join(outdir, 'graphs.zip'), 'r') as myzip:
                zipped_graphics = set([
                    info.filename for info in myzip.infolist()
                    if info.filename.endswith('.png')
                    or info.filename.endswith('.svg')
                ])
                expected_graphics = set(tsw_status_graphics_png +
                                        tsw_status_graphics_svg)

                for graphic in expected_graphics:
                    assert graphic in zipped_graphics

        assert os.path.isfile(
            os.path.join(outdir, globals.DEFAULT_TSW,
                         f'{globals.DEFAULT_TSW}_overview_status.png'))

    # delete output of test validations, clean up after ourselves
    def delete_run(self, run):
        # let's see if the output file gets cleaned up when the model is deleted

        ncfile = run.output_file.path
        outdir = os.path.dirname(ncfile)
        assert os.path.isfile(ncfile)
        run.delete()
        assert not os.path.exists(outdir)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:read_ts is deprecated, please use read instead:DeprecationWarning",
        "ignore: Too few points are available to generate:UserWarning")
    def test_validation(self):
        """ Test validation runs using different configurations """
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()

            # Custom setup for the validation run
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            # run.scaling_ref = ValidationRun.SCALE_REF
            run.scaling_method = ValidationRun.BETA_SCALING  # cdf matching
            run.scaling_ref = run.spatial_reference_configuration
            run.scaling_ref.is_scaling_reference = True
            run.scaling_ref.save()

            run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)

            run.save()

            for i, config in enumerate(run.dataset_configurations.all()):
                if config == run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ISMN_GOOD'))
                else:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

                config.save()

            pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='SCAN', \
                                        dataset_config=run.spatial_reference_configuration)
            pfilter.save()
            # add filterring according to depth_range with the default values:
            pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0,0.1", \
                                        dataset_config=run.spatial_reference_configuration)
            pfilter.save()

            run_id = run.id

            ## run the validation
            val.run_validation(run_id)
            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run.total_points == 9  # 9 ismn stations in hawaii testdata
            assert new_run.error_points == 0
            assert new_run.ok_points == 9

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=True,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    # TODO: fails, if validation contains temporal sub-windows. I suppose there is too little data to perform the temporal matching
    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:read_ts is deprecated, please use read instead:DeprecationWarning",
        "ignore: Too few points are available to generate:UserWarning")
    def test_validation_tcol(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'tcol').items():
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            # run.scaling_ref = ValidationRun.SCALE_REF
            run.plots_save_metadata = 'always'
            run.scaling_method = ValidationRun.BETA_SCALING  # cdf matching
            run.scaling_ref = run.spatial_reference_configuration
            run.scaling_ref.is_scaling_reference = True
            run.scaling_ref.save()

            run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)

            run.save()

            for config in run.dataset_configurations.all():
                if config == run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ISMN_GOOD'))
                else:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

                config.save()

            pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='SCAN', \
                                        dataset_config=run.spatial_reference_configuration)
            pfilter.save()

            # add filterring according to depth_range with the default values:
            pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0,0.1", \
                                        dataset_config=run.spatial_reference_configuration)
            pfilter.save()

            run_id = run.id

            # run the validation
            val.run_validation(run_id)
            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run.total_points == 9  # 9 ismn stations in hawaii testdata
            # at 5 locations the validation fails because not all datasets have data
            # assert new_run.error_points == 5
            assert new_run.error_points == testvalrun_data.results_tbe_dict()['test_validation_ccip_ref'][
                'new_run_error_points']
            # the other 4 are okay
            # assert new_run.ok_points == 4
            assert new_run.ok_points == testvalrun_data.results_tbe_dict()['test_validation_ccip_ref'][
                'new_run_ok_points']

            self.check_results(
                new_run,
                is_tcol_run=True,
                meta_plots=True,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:read_ts is deprecated, please use read instead:DeprecationWarning",
        "ignore: Too few points are available to generate:UserWarning")
    def test_validation_empty_network(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()

            run.plots_save_metadata = 'always'
            run.user = self.testuser

            # run.scaling_ref = ValidationRun.SCALE_REF
            run.scaling_method = ValidationRun.BETA_SCALING  # cdf matching
            run.scaling_ref = run.spatial_reference_configuration
            run.scaling_ref.is_scaling_reference = True
            run.scaling_ref.save()

            run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)

            run.save()

            for config in run.dataset_configurations.all():
                if config == run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ISMN_GOOD'))
                else:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

                config.save()

            # add filterring according to depth_range with values which cause that there is no points anymore:
            pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.1,0.2", \
                                        dataset_config=run.spatial_reference_configuration)
            pfilter.save()

            run_id = run.id

            ## run the validation
            val.run_validation(run_id)
            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run.total_points == 0
            assert new_run.error_points == 0
            assert new_run.ok_points == 0

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_gldas_ref(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()

            run.plots_save_metadata = 'always'
            run.user = self.testuser

            run.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name='GLDAS')
            run.spatial_reference_configuration.version = DatasetVersion.objects.get(
                short_name='GLDAS_NOAH025_3H_2_1')
            run.spatial_reference_configuration.variable = DataVariable.objects.get(
                pretty_name='GLDAS_SoilMoi0_10cm_inst')
            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_GLDAS_UNFROZEN'))
            run.spatial_reference_configuration.save()

            run.interval_from = datetime(2017, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)
            run.min_lat = self.hawaii_coordinates[0]
            run.min_lon = self.hawaii_coordinates[1]
            run.max_lat = self.hawaii_coordinates[2]
            run.max_lon = self.hawaii_coordinates[3]

            run.save()

            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            run_id = run.id

            ## run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run

            assert new_run.total_points == 19
            assert new_run.error_points == 0
            assert new_run.ok_points == 19

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=False,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_ccip_ref(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test not adapted to handle differing validation results with intra-annual metrics
                continue
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            run.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=globals.CCIP)
            run.spatial_reference_configuration.version = DatasetVersion.objects.get(
                short_name=globals.ESA_CCI_SM_P_V05_2)
            run.spatial_reference_configuration.variable = DataVariable.objects.get(
                pretty_name=globals.ESA_CCI_SM_P_sm)
            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

            run.spatial_reference_configuration.save()

            run.interval_from = datetime(2000, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2005, 1, 1, tzinfo=UTC)
            run.min_lat = self.hawaii_coordinates[0]
            run.min_lon = self.hawaii_coordinates[1]
            run.max_lat = self.hawaii_coordinates[2]
            run.max_lon = self.hawaii_coordinates[3]

            run.save()

            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    #                 config.filters.add(DataFilter.objects.get(name='FIL_C3S_FLAG_0'))
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            run_id = run.id

            ## run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)
            assert new_run

            assert new_run.total_points == 24, "Number of gpis is off"
            assert new_run.error_points == testvalrun_data.results_tbe_dict()['new_run_error_points'], "Error points are off"
            assert new_run.ok_points == testvalrun_data.results_tbe_dict()['new_run_ok_points'], "OK points are off"

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=False,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_ccia_ref(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test not adapted to handle differing validation results with intra-annual metrics
                continue
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            run.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=globals.CCIA)
            run.spatial_reference_configuration.version = DatasetVersion.objects.get(
                short_name=globals.ESA_CCI_SM_A_V06_1)
            run.spatial_reference_configuration.variable = DataVariable.objects.get(
                pretty_name=globals.ESA_CCI_SM_A_sm)
            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

            run.spatial_reference_configuration.save()

            run.interval_from = datetime(2000, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2005, 1, 1, tzinfo=UTC)
            run.min_lat = self.hawaii_coordinates[0]
            run.min_lon = self.hawaii_coordinates[1]
            run.max_lat = self.hawaii_coordinates[2]
            run.max_lon = self.hawaii_coordinates[3]

            run.save()

            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            run_id = run.id

            ## run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)
            assert new_run

            assert new_run.total_points == 24, "Number of gpis is off"
            assert new_run.error_points == 5, "Error points are off"
            assert new_run.ok_points == 19, "OK points are off"

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=False,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_smap_ref(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test not adapted to handle differing validation results with intra-annual metrics
                continue
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            run.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=globals.SMAP_L3)
            run.spatial_reference_configuration.version = DatasetVersion.objects.get(
                short_name=globals.SMAP_V5_PM)
            run.spatial_reference_configuration.variable = DataVariable.objects.get(
                pretty_name=globals.SMAP_soil_moisture)
            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

            run.spatial_reference_configuration.save()

            run.interval_from = datetime(2017, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)

            run.min_lat = self.hawaii_coordinates[0]
            run.min_lon = self.hawaii_coordinates[1]
            run.max_lat = self.hawaii_coordinates[2]
            run.max_lon = self.hawaii_coordinates[3]

            run.scaling_method = ValidationRun.MEAN_STD
            run.scaling_ref = run.spatial_reference_configuration
            run.scaling_ref.is_scaling_reference = True
            run.scaling_ref.save()

            run.save()

            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            run_id = run.id

            # run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run

            assert new_run.total_points == 140, "Number of gpis is off"
            assert new_run.error_points == 134, "Error points are off"
            assert new_run.ok_points == 6, "OK points are off"

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=False,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_ascat_ref(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test not adapted to handle differing validation results with intra-annual metrics
                continue
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            run.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=globals.ASCAT)
            run.spatial_reference_configuration.version = DatasetVersion.objects.get(
                short_name=globals.ASCAT_H113)
            run.spatial_reference_configuration.variable = DataVariable.objects.get(
                pretty_name=globals.ASCAT_sm)
            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

            run.spatial_reference_configuration.save()

            run.interval_from = datetime(2017, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)
            # different window is used here, because for the default one there is too much memory needed to create and save
            # plots
            run.min_lat = 20.32
            run.min_lon = -157.47
            run.max_lat = 21.33
            run.max_lon = -155.86

            run.scaling_method = ValidationRun.MEAN_STD
            run.scaling_ref = run.spatial_reference_configuration
            run.scaling_ref.is_scaling_reference = True
            run.scaling_ref.save()
            run.save()

            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            run_id = run.id
            ## run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run

            assert new_run.total_points == 15, "Number of gpis is off"
            assert new_run.error_points == 6, "Error points are off"
            assert new_run.ok_points == 9, "OK points are off"

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=False,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_c3s_ref(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test not adapted to handle differing validation results with intra-annual metrics
                continue
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            run.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=globals.C3SC)
            run.spatial_reference_configuration.version = DatasetVersion.objects.get(
                short_name=globals.C3S_V202012)
            run.spatial_reference_configuration.variable = DataVariable.objects.get(
                pretty_name=globals.C3S_sm)
            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

            run.spatial_reference_configuration.save()

            run.interval_from = datetime(2017, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)
            run.min_lat = self.hawaii_coordinates[0]
            run.min_lon = self.hawaii_coordinates[1]
            run.max_lat = self.hawaii_coordinates[2]
            run.max_lon = self.hawaii_coordinates[3]

            run.save()

            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            run_id = run.id

            ## run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run

            assert new_run.total_points == 24, "Number of gpis is off"
            assert new_run.error_points == 5, "Error points are off"
            assert new_run.ok_points == 19, "OK points are off"

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=False,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_era5_ref(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            run.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=globals.ERA5)
            run.spatial_reference_configuration.version = DatasetVersion.objects.get(
                short_name=globals.ERA5_20190613)
            run.spatial_reference_configuration.variable = DataVariable.objects.get(
                pretty_name=globals.ERA5_sm)
            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            #        run.spatial_reference_configuration.filters.add(DataFilter.objects.get(name='FIL_ERA5_TEMP_UNFROZEN'))

            run.spatial_reference_configuration.save()

            run.interval_from = datetime(2017, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)
            run.min_lat = self.hawaii_coordinates[0]
            run.min_lon = self.hawaii_coordinates[1]
            run.max_lat = self.hawaii_coordinates[2]
            run.max_lon = self.hawaii_coordinates[3]

            run.save()

            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            run_id = run.id

            ## run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run, "Didn't find validation in database"

            assert new_run.total_points == 11, "Number of gpis is off"
            assert new_run.error_points == 0, "Too many error gpis"
            assert new_run.ok_points == 11, "OK points are off"

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=False,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_ascat(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test not adapted to handle differing validation results with intra-annual metrics
                continue
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    config.dataset = Dataset.objects.get(short_name='ASCAT')
                    config.version = DatasetVersion.objects.get(
                        short_name='ASCAT_H113')
                    config.variable = DataVariable.objects.get(
                        pretty_name='ASCAT_sm')
                    config.filters.clear()
                    config.save()

            # run.scaling_ref = ValidationRun.SCALE_REF
            run.scaling_method = ValidationRun.BETA_SCALING  # cdf matching
            run.scaling_ref = run.spatial_reference_configuration
            run.scaling_ref.is_scaling_reference = True
            run.scaling_ref.save()

            run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)

            run.save()

            run_id = run.id

            ## run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run.total_points == 9
            assert new_run.error_points == 1
            assert new_run.ok_points == 8

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=True,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    # TODO: fails, if validation contains temporal sub-windows
    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    def test_validation_default(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test not adapted to handle differing validation results with intra-annual metrics
                continue
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            run.save()
            run_id = run.id

            ## run the validation
            val.run_validation(run_id)

            ## fetch results from db
            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run.total_points == 9
            assert new_run.error_points == 0
            assert new_run.ok_points == 9

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=True,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_anomalies_moving_avg(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():

            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser
            run.anomalies = ValidationRun.MOVING_AVG_35_D
            run.save()

            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            run.spatial_reference_configuration.save()
            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            run_id = run.id

            ## run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run
            assert new_run.total_points == 9
            assert new_run.error_points == 0
            assert new_run.ok_points == 9

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=True,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_anomalies_climatology(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():

            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()

            run.plots_save_metadata = 'always'
            run.user = self.testuser
            run.anomalies = ValidationRun.CLIMATOLOGY
            # make sure there is data for the climatology time period!
            run.anomalies_from = datetime(1978, 1, 1, tzinfo=UTC)
            run.anomalies_to = datetime(2018, 12, 31, 23, 59, 59)
            run.save()

            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            run.spatial_reference_configuration.save()
            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            run_id = run.id

            # run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=True,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    def test_nc_attributes(self):
        """
        Test correctness and completedness of netCDF attributes in the output file;
        a validation that doesn't involve ISMN ref is used to check the resolution attributes
        """
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()

            run.plots_save_metadata = 'always'
            run.user = self.testuser

            # need validation without ISMN as referebce to check resolution attributes
            run.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=globals.ERA5)
            run.spatial_reference_configuration.version = DatasetVersion.objects.get(
                short_name=globals.ERA5_20190613)
            run.spatial_reference_configuration.variable = DataVariable.objects.get(
                pretty_name=globals.ERA5_sm)
            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))

            run.spatial_reference_configuration.save()

            run.interval_from = datetime(2017, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)
            run.min_lat = self.hawaii_coordinates[0]
            run.min_lon = self.hawaii_coordinates[1]
            run.max_lat = self.hawaii_coordinates[2]
            run.max_lon = self.hawaii_coordinates[3]

            run.save()
            run_id = run.id
            # run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=False,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    # TODO: fails, if validation contains temporal sub-windows
    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    def test_c3s_validation_upscaling(self):
        """
        Test a validation of CCIP with ISMN as non-reference, and upscaling option active. All ISMN points are averaged
        and the results should produce 16 points (original c3s points); results are checked with `check_results`
        """
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'ismn_upscaling').items():

            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.user = self.testuser

            # hawaii bounding box
            run.min_lat = 18.625  # ll
            run.min_lon = -156.375  # ll
            run.max_lat = 20.375  # ur
            run.max_lon = -154.625  # ur

            # NOTE: ISMN non-reference points need to use one of the upscaling methods
            run.upscaling_method = "average"

            run.save()
            run_id = run.id
            # run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)
            assert new_run
            assert new_run.total_points == 16
            assert new_run.error_points == 12
            assert new_run.ok_points == 4

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=False,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    def validation_upscaling_for_dataset(self, ds, version, variable):
        """
        Generate a test with ISMN as non-reference dataset and the provided dataset, version, variable as reference.
        Test that the results and the output file with the function `check_results`
        """
        run = self.get_test_validation_run('ismn_upscaling')[TestValidationRunType.BULK_ISMN_UPSCALING].generate_val()
        run.user = self.testuser

        # NOTE: ISMN non-reference points need to use one of the upscaling methods
        run.upscaling_method = "average"

        # hawaii bounding box
        run.min_lat = 18.625  # ll
        run.min_lon = -156.375  # ll
        run.max_lat = 20.375  # ur
        run.max_lon = -154.625  # ur

        # NOTE: ISMN non-reference points need to use one of the upscaling methods
        run.upscaling = True
        run.spatial_reference_configuration.dataset = Dataset.objects.get(
            short_name=ds)
        run.spatial_reference_configuration.version = DatasetVersion.objects.get(
            short_name=version)
        run.spatial_reference_configuration.variable = DataVariable.objects.get(
            pretty_name=variable)
        run.save()
        run_id = run.id
        # run the validation
        val.run_validation(run_id)

        new_run = ValidationRun.objects.get(pk=run_id)
        assert new_run

        self.check_results(new_run, is_tcol_run=False, meta_plots=False)
        self.delete_run(new_run)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_all_datasets_validation_upscaling(self):
        """
        Test a validation for each sat. dataset with ISMN as non-reference, and upscaling option active. Test description
        in the function `validation_upscaling_for_dataset`
        """
        all_datasets = [(globals.CCIC, globals.ESA_CCI_SM_P_V05_2,
                         globals.ESA_CCI_SM_P_sm),
                        (globals.SMAP_L3, globals.SMAP_V5_PM,
                         globals.SMAP_soil_moisture),
                        (globals.ASCAT, globals.ASCAT_H113, globals.ASCAT_sm),
                        (globals.ERA5, globals.ERA5_20190613, globals.ERA5_sm),
                        (globals.GLDAS, globals.GLDAS_NOAH025_3H_2_1,
                         globals.GLDAS_SoilMoi0_10cm_inst)]

        for ds, version, variable in all_datasets:
            self.validation_upscaling_for_dataset(ds, version, variable)

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    def test_validation_upscaling_lut(self):
        """
        Test the function `create_upscaling_lut` in validation/batched.py by checking that the lookup table
        hase the expected dataset key and values to average. It also checks that when filters are applied to the
        non-reference dataset, the collected points change; in this case, with filters "COSMOS" and depth 0.0-0.1,
        no station in the ISMN is found
        """
        run = self.get_test_validation_run(
            'ismn_upscaling')[TestValidationRunType.BULK_ISMN_UPSCALING].generate_val()
        dataset = Dataset.objects.get(short_name='C3S_combined')
        version = DatasetVersion.objects.get(short_name="C3S_V202012")
        c3s_reader = val.create_reader(dataset, version)
        dataset = Dataset.objects.get(short_name='ISMN')
        version = DatasetVersion.objects.get(short_name="ISMN_V20180712_MINI")
        variable = DataVariable.objects.get(pretty_name="ISMN_soil_moisture")
        ismn_reader = val.create_reader(dataset, version)
        datasets = {
            "0-C3S_combined": {
                "class": c3s_reader
            },
            "1-ISMN": {
                "class": ismn_reader
            },
        }

        lut = create_upscaling_lut(validation_run=run,
                                   datasets=datasets,
                                   spatial_ref_name="0-C3S_combined")
        assert list(lut.keys()) == ["1-ISMN"]
        # the exact gpi number might change, so we only check that ismn points are averaged under three c3s pixels
        assert len(lut["1-ISMN"].values()) == 4

        data_filters = [
            DataFilter.objects.get(name="FIL_ALL_VALID_RANGE"),
            DataFilter.objects.get(name="FIL_ISMN_GOOD"),
        ]

        param_filters = [
            ParametrisedFilter(
                filter=DataFilter.objects.get(name="FIL_ISMN_NETWORKS"),
                parameters="COSMOS"),
            ParametrisedFilter(
                filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"),
                parameters="0.0,0.1")
        ]
        msk_reader, read_name, read_kwargs = val.setup_filtering(
            ismn_reader, data_filters, param_filters, dataset, variable)
        datasets = {
            "0-C3S_combined": {
                "class": c3s_reader
            },
            "1-ISMN": {
                "class": msk_reader
            },
        }
        lut = create_upscaling_lut(validation_run=run,
                                   datasets=datasets,
                                   spatial_ref_name="0-C3S_combined")
        assert list(lut.keys()) == ["1-ISMN"]
        assert lut["1-ISMN"] == []

    @pytest.mark.filterwarnings(
        "ignore:No results for gpi:UserWarning",
        "ignore:No data for:UserWarning",
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    def test_validation_spatial_subsetting(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():

            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            run = testvalrun_data.generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser

            # hawaii bounding box
            run.min_lat = 18.625  # ll
            run.min_lon = -156.375  # ll
            run.max_lat = 20.375  # ur
            run.max_lon = -154.625  # ur

            run.save()

            run.spatial_reference_configuration.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            run.spatial_reference_configuration.save()
            for config in run.dataset_configurations.all():
                if config != run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            run_id = run.id

            ## run the validation
            val.run_validation(run_id)

            new_run = ValidationRun.objects.get(pk=run_id)

            assert new_run
            assert new_run.total_points == 9
            assert new_run.error_points == 0
            assert new_run.ok_points == 9

            self.check_results(
                new_run,
                is_tcol_run=False,
                meta_plots=True,
                expected_results=testvalrun_data.results_tbe_dict())
            self.delete_run(new_run)

    def test_errors(self):
        dataset = Dataset()
        dataset.short_name = 'gibtsnicht'
        version = DatasetVersion()
        version.short_name = '-3.14'

        ## readers
        with pytest.raises(ValueError):
            no_reader = val.create_reader(dataset, version)

        ## save config
        validation_run = ValidationRun()
        val.save_validation_config(validation_run)

    def test_readers(self):
        start_time = time.time()

        datasets = Dataset.objects.all()
        for dataset in datasets:
            vs = dataset.versions.all()
            for version in vs:
                print("Testing {} version {}".format(dataset, version))

                reader = val.create_reader(dataset, version)

                if dataset.short_name == val.globals.ASCAT:
                    reader = val.BasicAdapter(reader)

                assert reader is not None
                if dataset.short_name == val.globals.ISMN:
                    data = reader.read(0)
                else:
                    data = reader.read(-155.42, 19.78)  ## hawaii
                assert data is not None
                assert isinstance(data, pd.DataFrame)

        print("Test duration: {}".format(time.time() - start_time))

    # minimal test of filtering, quicker than the full test below
    def test_setup_filtering_min(self):
        dataset = Dataset.objects.get(short_name='ISMN')
        version = DatasetVersion.objects.get(short_name='ISMN_V20180712_MINI')
        variable = DataVariable.objects.get(pretty_name='ISMN_soil_moisture')
        reader = val.create_reader(dataset, version)

        no_msk_reader, read_name, read_kwargs = \
            val.setup_filtering(reader, None, None, dataset, variable)
        assert no_msk_reader is not None
        data = getattr(no_msk_reader, read_name)(0, **read_kwargs)
        assert data is not None
        assert isinstance(data, pd.DataFrame)
        assert len(data.index) > 1
        assert not data[variable.short_name].empty

        data_filters = [
            DataFilter.objects.get(name="FIL_ALL_VALID_RANGE"),
            DataFilter.objects.get(name="FIL_ISMN_GOOD"),
        ]
        param_filters = [
            ParametrisedFilter(
                filter=DataFilter.objects.get(name="FIL_ISMN_NETWORKS"),
                parameters="  COSMOS , SCAN "),
            ParametrisedFilter(
                filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"),
                parameters="0.0,0.1")
        ]
        msk_reader, read_name, read_kwargs = \
            val.setup_filtering(reader, data_filters, param_filters, dataset,
                                variable)

        assert msk_reader is not None
        data = getattr(no_msk_reader, read_name)(0, **read_kwargs)
        assert data is not None
        assert isinstance(data, pd.DataFrame)
        assert len(data.index) > 1
        assert not data[variable.short_name].empty
        assert not np.any(data[variable.short_name].values < 0)
        assert not np.any(data[variable.short_name].values > 100)

    # test potential depth ranges errors
    def test_depth_range_filtering_errors(self):
        # perparing Validation run for ISMN
        run = ValidationRun()
        run.start_time = datetime.now(tzlocal())
        run.save()

        dataset = Dataset.objects.get(short_name='ISMN')
        version = dataset.versions.all()[0]

        ref_c = DatasetConfiguration()
        ref_c.validation = run
        ref_c.dataset = dataset
        ref_c.version = version
        ref_c.variable = dataset.variables.first()
        ref_c.save()
        run.spatial_reference_configuration = ref_c
        run.save()

        # adding filters where depth_to is smaller than depth_from
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.2,0.1", \
                                     dataset_config=run.spatial_reference_configuration)
        pfilter.save()

        ref_reader, read_name, read_kwargs = val.validation._get_spatial_reference_reader(
            run)

        with pytest.raises(ValueError, match=r".*than.*"):
            val.create_jobs(run, ref_reader,
                            run.spatial_reference_configuration)

        ParametrisedFilter.objects.all().delete()

        # adding filters with negative values
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="-0.05,0.1", \
                                     dataset_config=run.spatial_reference_configuration)
        pfilter.save()

        with pytest.raises(ValueError, match=r".*negative.*"):
            val.create_jobs(run, ref_reader,
                            run.spatial_reference_configuration)

        ParametrisedFilter.objects.all().delete()

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="-0.05,-0.1", \
                                     dataset_config=run.spatial_reference_configuration)
        pfilter.save()

        with pytest.raises(ValueError, match=r".*negative.*"):
            val.create_jobs(run, ref_reader,
                            run.spatial_reference_configuration)

        ParametrisedFilter.objects.all().delete()

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.05,-0.1", \
                                     dataset_config=run.spatial_reference_configuration)
        pfilter.save()

        with pytest.raises(ValueError, match=r".*negative.*"):
            val.create_jobs(run, ref_reader,
                            run.spatial_reference_configuration)

    def test_temporal_adapter(self):
        # test that the offset is used for the following datasets and versions
        for dt, ver, field, unit in [
            (globals.SMOS_L3, globals.SMOSL3_Level3_DESC,
             "Mean_Acq_Time_Seconds", "s"),
            (globals.SMOS_L3, globals.SMOSL3_Level3_ASC,
             "Mean_Acq_Time_Seconds", "s"),
            (globals.SMOS_IC, globals.SMOS_105_ASC, "UTC_Seconds", "s"),
        ]:
            dataset = Dataset.objects.get(short_name=dt)
            version = DatasetVersion.objects.get(short_name=ver)

            reader = val.create_reader(dataset, version)
            midnight_tstamp = reader.read(
                -155.42,
                19.78,
            )

            t_adaped_reader = adapt_timestamp(reader, dataset, version)
            exact_tstamp = t_adaped_reader.read(
                -155.42,
                19.78,
            )

            # Check that the values where the exact date is missing are dropped
            assert exact_tstamp.index.shape == \
                   midnight_tstamp[~np.isnan(midnight_tstamp[field])].index.shape
            # Check the index type
            assert exact_tstamp.index.dtype == np.dtype('<M8[ns]')
            # Check that the offset field is not in the output
            assert field not in exact_tstamp.columns

    # test all combinations of datasets, versions, variables, and filters
    @pytest.mark.long_running
    def test_setup_filtering_max(self):
        start_time = time.time()

        for i, dataset in enumerate(Dataset.objects.all()):
            self.__logger.info(dataset.pretty_name)
            vs = dataset.versions.all()
            va = dataset.variables.all()

            for version in vs:
                reader = val.create_reader(dataset, version)
                fils = version.filters.all()
                for variable in va:
                    for data_filter in fils:
                        self.__logger.debug(
                            "Testing {} version {} variable {} filter {}".
                            format(dataset, version, variable,
                                   data_filter.name))
                        if data_filter.parameterised:
                            pfilter = ParametrisedFilter(
                                filter=data_filter,
                                parameters=data_filter.default_parameter)

                            msk_reader, read_name, read_kwargs = \
                                val.setup_filtering(reader, [], [pfilter], dataset, variable)

                        else:
                            msk_reader, read_name, read_kwargs = \
                                val.setup_filtering(reader, [data_filter], [], dataset, variable)

                        assert msk_reader is not None
                        if dataset.short_name == val.globals.ISMN:
                            data = getattr(msk_reader,
                                           read_name)(0, **read_kwargs)
                        else:
                            data = getattr(msk_reader,
                                           read_name)(-155.42, 19.78,
                                                      **read_kwargs)  ## hawaii
                        assert data is not None
                        assert variable.short_name in data.columns
                        assert isinstance(data, pd.DataFrame)

                        # handles the case where all values are flagged (i.e. for SMOS L3)
                        if not len(data.index) > 1 or data[
                                variable.short_name].empty:
                            unfiltered = reader.read(-155.42, 19.78,
                                                     **read_kwargs)
                            assert unfiltered.count()[
                                variable.short_name] == len(
                                    unfiltered[variable.short_name].dropna())

        print("Test duration: {}".format(time.time() - start_time))

    def _check_jobs(self, total_points, jobs, metadata_present=False):
        assert jobs
        assert total_points > 0
        assert len(jobs) > 0
        gpisum = 0
        for job in jobs:
            if metadata_present:
                assert len(job) == 4
            else:
                assert len(job) == 3
            if np.isscalar(job[0]):
                assert np.isscalar(job[1])
                assert np.isscalar(job[2])
                gpisum += 1
            else:
                numgpis = len(job[0])
                gpisum += numgpis
                assert numgpis > 0
                assert len(job[1]) == numgpis
                assert len(job[2]) == numgpis

        assert total_points == gpisum

    def test_create_jobs(self):
        for dataset in Dataset.objects.all():
            self.__logger.info(dataset.short_name)
            vs = dataset.versions.all()

            for version in vs:
                run = ValidationRun()
                run.start_time = datetime.now(tzlocal())
                run.save()

                ref_c = DatasetConfiguration()
                ref_c.validation = run
                ref_c.dataset = dataset
                ref_c.version = version
                ref_c.variable = dataset.variables.first()
                ref_c.save()

                run.spatial_reference_configuration = ref_c
                run.save()

                ref_reader, read_name, read_kwargs = val.validation._get_spatial_reference_reader(
                    run)

                total_points, jobs = val.create_jobs(
                    run, ref_reader, run.spatial_reference_configuration)

                if dataset.short_name == "ISMN":
                    self._check_jobs(total_points, jobs, metadata_present=True)
                else:
                    self._check_jobs(total_points, jobs)

    def test_geographic_subsetting(self):
        # hawaii bounding box
        min_lat = 18.625  # ll
        min_lon = -156.375  # ll
        max_lat = 20.375  # ur
        max_lon = -154.625  # ur

        # we need the reader just to get the grid
        dataset = Dataset.objects.get(short_name='C3S_combined')
        version = DatasetVersion.objects.get(short_name='C3S_V201812')
        c3s_reader = val.create_reader(dataset, version)
        # apply Basic Adapter only
        c3s_reader, _, _ = val.setup_filtering(
            c3s_reader,
            filters=None,
            param_filters=None,
            dataset=dataset,
            variable=DataVariable.objects.get(pretty_name='C3S_sm'))

        gpis, lons, lats, cells = c3s_reader.cls.grid.get_grid_points()

        subgpis, sublons, sublats, subindex = _geographic_subsetting(
            gpis, lons, lats, min_lat, min_lon, max_lat, max_lon)

        assert len(subgpis) == 16
        assert len(sublats) == len(subgpis)
        assert len(sublons) == len(subgpis)

        assert not np.any(sublats > max_lat), "subsetting error: max_lat"
        assert not np.any(sublats < min_lat), "subsetting error: min_lat"
        assert not np.any(sublons > max_lon), "subsetting error: max_lon"
        assert not np.any(sublons < min_lon), "subsetting error: min_lon"

    def test_no_geographic_subsetting(self):
        # we need the reader just to get the grid
        dataset = Dataset.objects.get(short_name='C3S_combined')
        version = DatasetVersion.objects.get(short_name='C3S_V201812')
        c3s_reader = val.create_reader(dataset, version)
        # apply Basic Adapter only
        c3s_reader, _, _ = val.setup_filtering(
            c3s_reader,
            filters=None,
            param_filters=None,
            dataset=dataset,
            variable=DataVariable.objects.get(pretty_name='C3S_sm'))

        gpis, lats, lons, cells = c3s_reader.cls.grid.get_grid_points()

        subgpis, sublats, sublons, subindex = _geographic_subsetting(
            gpis, lats, lons, None, None, None, None)

        assert np.array_equal(gpis, subgpis)
        assert np.array_equal(lats, sublats)
        assert np.array_equal(lons, sublons)

    def test_geographic_subsetting_across_dateline(self):
        test_coords = [
            (-34.30, -221.13, 80.17, -111.44),  # dateline left
            (-58.81, 127.61, 77.15, 256.99)  # dateline right
        ]

        russia_gpi = 898557
        russia_gpi2 = 898567

        for min_lat, min_lon, max_lat, max_lon in test_coords:
            dataset = Dataset.objects.get(short_name='C3S_combined')
            version = DatasetVersion.objects.get(short_name='C3S_V201812')

            c3s_reader = val.create_reader(dataset, version)
            # apply Basic Adapter only
            c3s_reader, _, _ = val.setup_filtering(
                c3s_reader,
                filters=None,
                param_filters=None,
                dataset=dataset,
                variable=DataVariable.objects.get(pretty_name='C3S_sm'))

            gpis, lats, lons, cells = c3s_reader.cls.grid.get_grid_points()

            subgpis, sublats, sublons, subindex = _geographic_subsetting(
                gpis, lats, lons, min_lat, min_lon, max_lat, max_lon)

            assert len(subgpis) > 100
            assert len(sublats) == len(subgpis)
            assert len(sublons) == len(subgpis)
            assert russia_gpi in subgpis
            assert russia_gpi2 in subgpis

    def test_geographic_subsetting_shifted(self):
        ## leaflet allows users to shift the map arbitrarily to the left or right. Check that we can compensate for that
        dataset = Dataset.objects.get(short_name='C3S_combined')
        version = DatasetVersion.objects.get(short_name='C3S_V201812')

        c3s_reader = val.create_reader(dataset, version)
        # apply Basic Adapter only
        c3s_reader, _, _ = val.setup_filtering(
            c3s_reader,
            filters=None,
            param_filters=None,
            dataset=dataset,
            variable=DataVariable.objects.get(pretty_name='C3S_sm'))

        gpis, lats, lons, cells = c3s_reader.cls.grid.get_grid_points()

        test_coords = [
            (-46.55, -1214.64, 71.96, -1105.66, 1),  # americas
            (9.79, -710.50, 70.14, -545.27, 2),  # asia
            (-55.37, 1303.24, 68.39, 1415.03, 1),  # americas
            (7.01, 1473.39, 68.39, 1609.80, 2),  # asia
        ]

        panama_gpi = 566315
        india_gpi = 683588

        for min_lat, min_lon, max_lat, max_lon, area in test_coords:
            subgpis, sublats, sublons, subindex = _geographic_subsetting(
                gpis, lats, lons, min_lat, min_lon, max_lat, max_lon)

            assert len(subgpis) > 100
            assert len(sublats) == len(subgpis)
            assert len(sublons) == len(subgpis)
            if area == 1:
                assert panama_gpi in subgpis
            elif area == 2:
                assert india_gpi in subgpis

    def test_mkdir_exception(self):
        with pytest.raises(PermissionError):
            val.mkdir_if_not_exists('/root/valentina_unit_test')

    def test_first_file_in_nothing_found(self):
        result = val.first_file_in(
            '/tmp', 'there_really_should_be_no_extension_like_this')
        assert result is None

    def test_count_gpis_exception(self):
        num = val.num_gpis_from_job(None)
        assert num == 1

    @pytest.mark.filterwarnings(
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    @pytest.mark.graphs
    def test_generate_graphs_ismn_no_meta(self):
        # Note: parameterized tests don't really work in this case
        infile, short_name = ('testdata/output_data/c3s_ismn.nc', 'ISMN')
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test file does not contain intra-annual data
                continue

            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            # create validation object and data folder for it
            v = testvalrun_data.generate_val()

            # scatterplot
            v.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=short_name)
            v.spatial_reference_configuration.save()
            run_dir = path.join(OUTPUT_FOLDER, str(v.id))
            val.mkdir_if_not_exists(run_dir)

            # copy our netcdf data file there and link it in the validation object
            # then generate the graphs
            shutil.copy(infile, path.join(run_dir, 'results.nc'))
            val.set_outfile(v, run_dir)
            v.save()
            val.generate_all_graphs(
                validation_run=v,
                temporal_sub_windows=testvalrun_data.
                results_tbe_dict()['temporal_sub_windows'],
                outfolder=run_dir,
                save_metadata='never',
            )

            for tsw in testvalrun_data.results_tbe_dict()[
                    'temporal_sub_windows']:
                boxplot_pngs = [
                    x for x in os.listdir(os.path.join(run_dir, tsw))
                    if fnmatch.fnmatch(x, f'{tsw}_boxplot*.png')
                ]
                self.__logger.debug(boxplot_pngs)
                # no boxplot for status
                n_metrics = len(globals.METRICS.keys()) - 1
                assert len(boxplot_pngs) == n_metrics

                overview_pngs = [
                    x for x in os.listdir(os.path.join(run_dir, tsw))
                    if fnmatch.fnmatch(x, f'{tsw}_overview*.png')
                ]
                self.__logger.debug(overview_pngs)
                assert len(overview_pngs) == n_metrics * (
                    v.dataset_configurations.count() - 1)

            self.delete_run(v)

    @pytest.mark.filterwarnings(
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    @pytest.mark.graphs
    def test_generate_graphs_ismn_metadata(self):
        """
        Create plots from example validation run that also contains the ISMN
        metadata based plots for: LC class, KG class, soil props, frm class.
        When more metadata plots are added (globals), exchange reference file!
        """
        # Note: parameterized tests don't really work in this case
        infile, short_name = ('testdata/output_data/c3s_ismn_metadata.nc',
                              'ISMN')
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test file does not contain intra-annual data
                continue

            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            # create validation object and data folder for it
            v = testvalrun_data.generate_val()

            # scatterplot
            v.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=short_name)
            v.spatial_reference_configuration.save()
            run_dir = path.join(OUTPUT_FOLDER, str(v.id))
            val.mkdir_if_not_exists(run_dir)

            # copy our netcdf data file there and link it in the validation object
            # then generate the graphs
            shutil.copy(infile, path.join(run_dir, 'results.nc'))
            val.set_outfile(v, run_dir)
            v.save()
            val.generate_all_graphs(
                validation_run=v,
                temporal_sub_windows=testvalrun_data.
                results_tbe_dict()['temporal_sub_windows'],
                outfolder=run_dir,
                save_metadata='always',
            )

            n_metrics = len(globals.METRICS.keys())
            n_metas = len(globals.METADATA_PLOT_NAMES.keys())

            meta_boxplot_pngs = [
                x for x in os.listdir(run_dir)
                if fnmatch.fnmatch(x, 'boxplot*_metadata_*.png')
            ]
            self.__logger.debug(meta_boxplot_pngs)
            # no meta box plots for r_p & rho_p
            assert len(meta_boxplot_pngs) == (n_metrics - 3) * n_metas

            boxplot_pngs = [
                x for x in os.listdir(run_dir)
                if fnmatch.fnmatch(x, 'boxplot*.png')
            ]
            self.__logger.debug(boxplot_pngs)
            # no boxplot for status
            assert len(boxplot_pngs) == n_metrics - 1 + (n_metas *
                                                         (n_metrics - 3))

            overview_pngs = [
                x for x in os.listdir(run_dir)
                if fnmatch.fnmatch(x, 'overview*.png')
            ]
            self.__logger.debug(overview_pngs)
            assert len(overview_pngs) == n_metrics * (
                v.dataset_configurations.count() - 1)

            self.delete_run(v)

    @pytest.mark.filterwarnings(
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    @pytest.mark.graphs
    def test_generate_graphs_gldas(self):
        infile, short_name = ('testdata/output_data/c3s_gldas.nc', 'GLDAS')
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test file does not contain intra-annual data
                continue

            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            # create validation object and data folder for it
            v = testvalrun_data.generate_val()
            v.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=short_name)
            v.spatial_reference_configuration.save()
            run_dir = path.join(OUTPUT_FOLDER, str(v.id))
            val.mkdir_if_not_exists(run_dir)

            shutil.copy(infile, path.join(run_dir, 'results.nc'))
            val.set_outfile(v, run_dir)
            v.save()
            val.generate_all_graphs(
                validation_run=v,
                temporal_sub_windows=testvalrun_data.
                results_tbe_dict()['temporal_sub_windows'],
                outfolder=run_dir,
                save_metadata='never',
            )

            boxplot_pngs = [
                x for x in os.listdir(run_dir)
                if fnmatch.fnmatch(x, 'boxplot*.png')
            ]
            self.__logger.debug(boxplot_pngs)
            # no boxplot for status
            n_metrics = len(globals.METRICS.keys()) - 1
            assert len(boxplot_pngs) == n_metrics

            overview_pngs = [
                x for x in os.listdir(run_dir)
                if fnmatch.fnmatch(x, 'overview*.png')
            ]
            self.__logger.debug(overview_pngs)
            assert len(overview_pngs) == n_metrics * (
                v.dataset_configurations.count() - 1)

            self.delete_run(v)

    @pytest.mark.filterwarnings(
        "ignore: Too few points are available to generate:UserWarning")
    @pytest.mark.long_running
    @pytest.mark.graphs
    def test_generate_graphs_era5land(self):
        infile, short_name = ('testdata/output_data/c3s_era5land.nc',
                              'ERA5_LAND')
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            if testvalrun_type != 'default_bulk':  # test file does not contain intra-annual data
                continue

            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            # create validation object and data folder for it
            v = testvalrun_data.generate_val()
            v.spatial_reference_configuration.dataset = Dataset.objects.get(
                short_name=short_name)
            v.spatial_reference_configuration.save()
            run_dir = path.join(OUTPUT_FOLDER, str(v.id))
            val.mkdir_if_not_exists(run_dir)

            shutil.copy(infile, path.join(run_dir, 'results.nc'))
            val.set_outfile(v, run_dir)
            v.save()
            val.generate_all_graphs(
                validation_run=v,
                temporal_sub_windows=testvalrun_data.
                results_tbe_dict()['temporal_sub_windows'],
                outfolder=run_dir,
                save_metadata='never',
            )

            boxplot_pngs = [
                x for x in os.listdir(run_dir)
                if fnmatch.fnmatch(x, 'boxplot*.png')
            ]
            self.__logger.debug(boxplot_pngs)
            n_metrics = len(
                globals.METRICS.keys()) - 1  # no boxplot for status
            assert len(boxplot_pngs) == n_metrics

            overview_pngs = [
                x for x in os.listdir(run_dir)
                if fnmatch.fnmatch(x, 'overview*.png')
            ]
            self.__logger.debug(overview_pngs)
            assert len(overview_pngs) == n_metrics * (
                v.dataset_configurations.count() - 1)

            self.delete_run(v)

    # @pytest.mark.long_running
    def test_existing_validations(self):
        # common default settings:
        user = self.testuser
        time_intervals_from = datetime(1978, 1, 1, tzinfo=UTC)
        time_intervals_to = datetime(2018, 12, 31, tzinfo=UTC)
        anomalies_methods = ValidationRun.ANOMALIES_METHODS
        scaling_methods = [
            ValidationRun.MIN_MAX, ValidationRun.NO_SCALING,
            ValidationRun.MEAN_STD
        ]
        run_ids = []
        # preparing a few validations, so that there is a base to be searched
        for i in range(3):
            self.__logger.info(f"{self.get_test_validation_run('default')=}")
            run = self.get_test_validation_run(
                'default')[TestValidationRunType.DEFAULT_BULK].generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser
            run.interval_from = time_intervals_from
            run.interval_to = time_intervals_to
            run.min_lat = self.hawaii_coordinates[0]
            run.min_lon = self.hawaii_coordinates[1]
            run.max_lat = self.hawaii_coordinates[2]
            run.max_lon = self.hawaii_coordinates[3]

            run.anomalies = anomalies_methods[i][0]
            if anomalies_methods[i][0] == 'climatology':
                run.anomalies_from = time_intervals_from
                run.anomalies_to = time_intervals_to
            run.scaling_method = scaling_methods[i]
            if run.scaling_method != 'none':
                run.scaling_ref = run.spatial_reference_configuration
                run.scaling_ref.is_scaling_reference = True
                run.scaling_ref.save()
            run.doi = f'doi-1-2-{i}'
            run.save()
            run_ids.append(run.id)

        # ================== tcols ====================================
        run_tcol = self.get_test_validation_run(
            'tcol')[TestValidationRunType.DEFAULT_TCOL_BULK].generate_val()
        run_tcol.user = self.testuser
        run_tcol.interval_from = time_intervals_from
        run_tcol.interval_to = time_intervals_to
        run_tcol.min_lat = self.hawaii_coordinates[0]
        run_tcol.min_lon = self.hawaii_coordinates[1]
        run_tcol.max_lat = self.hawaii_coordinates[2]
        run_tcol.max_lon = self.hawaii_coordinates[3]

        run_tcol.anomalies = anomalies_methods[0][0]
        run_tcol.scaling_method = scaling_methods[0]
        run_tcol.scaling_ref = run.spatial_reference_configuration
        run_tcol.scaling_ref.is_scaling_reference = True
        run_tcol.scaling_ref.save()

        run_tcol.doi = f'tcol_doi-1-2-3'
        run_tcol.save()
        run_tcol_id = run_tcol.id

        # ========= validations with filters

        run_filt = self.get_test_validation_run(
            'default')[TestValidationRunType.DEFAULT_BULK].generate_val()
        run_filt.user = self.testuser
        run_filt.interval_from = time_intervals_from
        run_filt.interval_to = time_intervals_to
        run_filt.min_lat = self.hawaii_coordinates[0]
        run_filt.min_lon = self.hawaii_coordinates[1]
        run_filt.max_lat = self.hawaii_coordinates[2]
        run_filt.max_lon = self.hawaii_coordinates[3]

        run_filt.anomalies = anomalies_methods[0][0]
        run_filt.scaling_method = scaling_methods[0]
        run_filt.scaling_ref = run.spatial_reference_configuration
        run_filt.scaling_ref.is_scaling_reference = True
        run_filt.scaling_ref.save()

        run_filt.doi = f'doi-1-2-8'
        run_filt.save()
        run_filt_id = run_filt.id

        for config in run_filt.dataset_configurations.all():
            config.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            if config.dataset.short_name == globals.ISMN:
                config.filters.add(
                    DataFilter.objects.get(name='FIL_ISMN_GOOD'))

        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='SCAN', \
                                     dataset_config=run_filt.spatial_reference_configuration)
        pfilter.save()
        pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0,0.1", \
                                     dataset_config=run_filt.spatial_reference_configuration)
        pfilter.save()

        published_runs = ValidationRun.objects.exclude(
            doi='').order_by('-start_time')

        # here will be validations for asserting, I start with exactly the same validations and check if it finds them:
        for i in range(3):
            run = self.get_test_validation_run(
                'default')[TestValidationRunType.DEFAULT_BULK].generate_val()
            run.plots_save_metadata = 'always'
            run.user = self.testuser
            run.interval_from = time_intervals_from
            run.interval_to = time_intervals_to
            run.min_lat = self.hawaii_coordinates[0]
            run.min_lon = self.hawaii_coordinates[1]
            run.max_lat = self.hawaii_coordinates[2]
            run.max_lon = self.hawaii_coordinates[3]

            run.anomalies = anomalies_methods[i][0]
            if anomalies_methods[i][0] == 'climatology':
                run.anomalies_from = time_intervals_from
                run.anomalies_to = time_intervals_to
            run.scaling_method = scaling_methods[i]
            if run.scaling_method != 'none':
                run.scaling_ref = run.spatial_reference_configuration
                run.scaling_ref.is_scaling_reference = True
                run.scaling_ref.save()
            run.save()
            is_there_one = compare_validation_runs(run, published_runs, user)

            assert is_there_one['is_there_validation']
            assert is_there_one['val_id'] == run_ids[i]
            run.delete()

        # runs to fail:
        run = self.get_test_validation_run(
            'default')[TestValidationRunType.DEFAULT_BULK].generate_val()
        run.plots_save_metadata = 'always'
        run.user = self.testuser
        run.interval_from = time_intervals_from
        run.interval_to = time_intervals_to

        # here different coordinates
        run.min_lat = 34
        run.min_lon = -11
        run.max_lat = 48
        run.max_lon = 71

        run.anomalies = anomalies_methods[0][0]
        run.scaling_method = scaling_methods[0]
        run.scaling_ref = run.spatial_reference_configuration
        run.scaling_ref.is_scaling_reference = True
        run.save()

        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # getting back to good coordinates
        run.min_lat = self.hawaii_coordinates[0]
        run.min_lon = self.hawaii_coordinates[1]
        run.max_lat = self.hawaii_coordinates[2]
        run.max_lon = self.hawaii_coordinates[3]

        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']
        assert is_there_one['val_id'] == run_ids[0]

        # spoiling time span:
        run.interval_from = datetime(1990, 1, 1, tzinfo=UTC)
        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        run.interval_from = time_intervals_from
        run.interval_to = datetime(2000, 1, 1, tzinfo=UTC)
        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # time span restored
        run.interval_to = time_intervals_to
        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']
        assert is_there_one['val_id'] == run_ids[0]

        # spoiling anomalies and scaling (there is no validation with anomalies set to 35 days average and min_max
        # scaling method at the same time):
        run.anomalies = anomalies_methods[1][0]
        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        run.anomalies = anomalies_methods[0][0]
        # there is no run with scaling method LINREG
        run.scaling_method = ValidationRun.LINREG
        run.scaling_ref = run.spatial_reference_configuration
        run.scaling_ref.is_scaling_reference = True
        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # restoring existing validation
        run.anomalies = anomalies_methods[2][0]
        run.scaling_method = scaling_methods[2]
        run.scaling_ref = run.spatial_reference_configuration
        run.scaling_ref.is_scaling_reference = True
        run.scaling_ref.save()

        run.anomalies_from = time_intervals_from
        run.anomalies_to = time_intervals_to
        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']
        assert is_there_one['val_id'] == run_ids[2]

        # messing up with anomalies time interval:
        run.anomalies_from = datetime(1990, 1, 1, tzinfo=UTC)
        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        run.anomalies_from = time_intervals_from
        run.anomalies_to = datetime(1990, 1, 1, tzinfo=UTC)
        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # getting back to appropriate settings
        run.anomalies_to = time_intervals_to
        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # getting back to settings of the run with filters set adding filters for the run
        run.anomalies = anomalies_methods[0][0]
        run.scaling_method = scaling_methods[0]
        run.scaling_ref = run.spatial_reference_configuration
        run.scaling_ref.is_scaling_reference = True
        run.scaling_ref.save()

        run.anomalies_from = None
        run.anomalies_to = None
        run.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # adding filters
        for new_config in run.dataset_configurations.all():
            new_config.filters.add(
                DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
            if new_config.dataset.short_name == globals.ISMN:
                new_config.filters.add(
                    DataFilter.objects.get(name='FIL_ISMN_GOOD'))

            new_config.save()

        new_pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='SCAN', \
                                         dataset_config=run.spatial_reference_configuration)
        new_pfilter.save()
        # add filterring according to depth_range with the default values:
        new_pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0,0.1", \
                                         dataset_config=run.spatial_reference_configuration)
        new_pfilter.save()
        is_there_one = compare_validation_runs(run, published_runs, user)

        assert is_there_one['is_there_validation']
        assert is_there_one['val_id'] == run_filt_id

        # messing up with filters:

        # adding filter for C3S
        c3s_filter = DataFilter.objects.get(name='FIL_C3S_MODE_ASC')
        for new_config in run.dataset_configurations.all():
            if new_config.dataset.short_name == globals.C3SC:
                new_config.filters.add(c3s_filter)
                new_config.save()
        is_there_one = compare_validation_runs(run, published_runs, user)

        assert not is_there_one['is_there_validation']

        # getting back to the right settings
        for new_config in run.dataset_configurations.all():
            if new_config.dataset.short_name == globals.C3SC:
                new_config.filters.remove(c3s_filter)
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # removing ismn filter:
        ismn_filter = DataFilter.objects.get(name='FIL_ISMN_GOOD')
        for new_config in run.dataset_configurations.all():
            if new_config.dataset.short_name == globals.ISMN:
                new_config.filters.remove(ismn_filter)

        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # restoring the filter:
        for new_config in run.dataset_configurations.all():
            if new_config.dataset.short_name == globals.ISMN:
                new_config.filters.add(ismn_filter)
            new_config.save()
        is_there_one = compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # messing up with parameterised filters:
        # ... with networks
        for pf in ParametrisedFilter.objects.filter(
                dataset_config=run.spatial_reference_configuration):
            if DataFilter.objects.get(
                    pk=pf.filter_id).name == 'FIL_ISMN_NETWORKS':
                pf.parameters = 'SCAN,OZNET'
                pf.save()

        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        for pf in ParametrisedFilter.objects.filter(
                dataset_config=run.spatial_reference_configuration):
            if DataFilter.objects.get(
                    pk=pf.filter_id).name == 'FIL_ISMN_NETWORKS':
                pf.parameters = 'OZNET'
                pf.save()

        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # restoring networks
        for pf in ParametrisedFilter.objects.filter(
                dataset_config=run.spatial_reference_configuration):
            if DataFilter.objects.get(
                    pk=pf.filter_id).name == 'FIL_ISMN_NETWORKS':
                pf.parameters = 'SCAN'
                pf.save()

        is_there_one = compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # with depths
        for pf in ParametrisedFilter.objects.filter(
                dataset_config=run.spatial_reference_configuration):
            if DataFilter.objects.get(
                    pk=pf.filter_id).name == 'FIL_ISMN_DEPTH':
                pf.parameters = '0.10,0.20'
                pf.save()

        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # restoring depths
        for pf in ParametrisedFilter.objects.filter(
                dataset_config=run.spatial_reference_configuration):
            if DataFilter.objects.get(
                    pk=pf.filter_id).name == 'FIL_ISMN_DEPTH':
                pf.parameters = '0.0,0.1'
                pf.save()

        is_there_one = compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # adding a new dataset:
        data_c = DatasetConfiguration()
        data_c.validation = run
        data_c.dataset = Dataset.objects.get(short_name='ASCAT')
        data_c.version = DatasetVersion.objects.get(short_name='ASCAT_H113')
        data_c.variable = DataVariable.objects.get(pretty_name='ASCAT_sm')
        data_c.save()

        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        data_c.delete()

        is_there_one = compare_validation_runs(run, published_runs, user)
        assert is_there_one['is_there_validation']

        # checking scaling reference:
        new_ref = run.dataset_configurations.all()[0]
        run.scaling_ref = new_ref
        run.save()

        is_there_one = compare_validation_runs(run, published_runs, user)
        assert not is_there_one['is_there_validation']

        # ================== tcols ====================================
        run_tcol = self.get_test_validation_run(
            'tcol')[TestValidationRunType.DEFAULT_TCOL_BULK].generate_val()
        run_tcol.user = self.testuser
        run_tcol.interval_from = time_intervals_from
        run_tcol.interval_to = time_intervals_to
        run_tcol.min_lat = self.hawaii_coordinates[0]
        run_tcol.min_lon = self.hawaii_coordinates[1]
        run_tcol.max_lat = self.hawaii_coordinates[2]
        run_tcol.max_lon = self.hawaii_coordinates[3]

        run_tcol.anomalies = anomalies_methods[0][0]
        run_tcol.scaling_method = scaling_methods[0]
        run_tcol.scaling_ref = run.spatial_reference_configuration
        run_tcol.scaling_ref.is_scaling_reference = True
        run_tcol.scaling_ref.save()

        run_tcol.save()
        is_there_one = compare_validation_runs(run_tcol, published_runs, user)

        assert is_there_one['is_there_validation']
        assert is_there_one['val_id'] == run_tcol_id

        # setting tcols to False
        run_tcol.tcol = False
        run_tcol.save()

        is_there_one = compare_validation_runs(run_tcol, published_runs, user)
        assert not is_there_one['is_there_validation']

        ValidationRun.objects.all().delete()
        DatasetConfiguration.objects.all().delete()
        ParametrisedFilter.objects.all().delete()

    #TODO: does not run with temporal subwindows
    def test_copy_validation(self):
        for testvalrun_type, testvalrun_data in self.get_test_validation_run(
                'default').items():
            # if testvalrun_type != 'default_bulk':  # test file does not contain intra-annual data
            #     continue

            self.__logger.debug(
                f"Running test '{get_function_name()}' for {testvalrun_type}")

            # create validation object and data folder for it
            run = testvalrun_data.generate_val()

            run.plots_save_metadata = 'always'
            run.user = self.testuser

            run.scaling_method = ValidationRun.MEAN_STD
            run.scaling_ref = run.spatial_reference_configuration
            run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
            run.interval_to = datetime(2018, 12, 31, tzinfo=UTC)
            run.save()

            run.scaling_ref.is_scaling_reference = True
            run.scaling_ref.save()

            for config in run.dataset_configurations.all():
                if config == run.spatial_reference_configuration:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ISMN_GOOD'))
                else:
                    config.filters.add(
                        DataFilter.objects.get(name='FIL_ALL_VALID_RANGE'))
                config.save()

            pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name='FIL_ISMN_NETWORKS'), parameters='SCAN', \
                                        dataset_config=run.spatial_reference_configuration)
            pfilter.save()
            pfilter = ParametrisedFilter(filter=DataFilter.objects.get(name="FIL_ISMN_DEPTH"), parameters="0.0,0.1", \
                                        dataset_config=run.spatial_reference_configuration)
            pfilter.save()
            run_id = run.id
            val.run_validation(run_id)
            new_run = get_object_or_404(ValidationRun, pk=run_id)
            copied_run_info = copy_validationrun(new_run, self.testuser)
            assert copied_run_info['run_id'] == run_id

            validations = ValidationRun.objects.exclude(
                pk=copied_run_info['run_id'])
            copied_run = ValidationRun.objects.get(
                pk=copied_run_info['run_id'])
            comparison = compare_validation_runs(copied_run, validations,
                                                 copied_run.user)

            # the query validations will be empty so 'is_there_validation' == False, 'val_id' == None, '
            # 'belongs_to_user'==False, 'is_published' == False
            assert not comparison['is_there_validation']
            assert comparison['val_id'] is None
            assert not comparison['belongs_to_user']
            assert not comparison['is_published']

            copied_run_info = copy_validationrun(new_run, self.testuser2)
            assert copied_run_info['run_id'] != run.id

            validations = ValidationRun.objects.exclude(
                pk=copied_run_info['run_id'])
            copied_run = ValidationRun.objects.get(
                pk=copied_run_info['run_id'])

            comparison = compare_validation_runs(copied_run, validations,
                                                 copied_run.user)

            # print(f'\n\t{comparison}\n')
            assert comparison['is_there_validation']
            assert comparison['val_id'] == run.id
            assert not comparison['belongs_to_user']
            assert not comparison['is_published']

            assert copied_run.total_points == 9
            assert copied_run.error_points == 0
            assert copied_run.ok_points == 9

            self.check_results(
                copied_run,
                is_tcol_run=False,
                meta_plots=True,
                expected_results=testvalrun_data.results_tbe_dict())

            # copying again, so to check CopiedValidations model
            new_run = get_object_or_404(ValidationRun, pk=run_id)
            copy_validationrun(new_run, self.testuser2)

            # checking if saving to CopiedValidations model is correct (should be 2, because the first validation was
            # returned the same, and only the second and the third one were copied:
            copied_runs = CopiedValidations.objects.all()
            assert len(copied_runs) == 2
            assert copied_runs[0].used_by_user == self.testuser2

            # removing the original run should not cause removal of the record
            original_run = copied_runs[0].original_run
            self.delete_run(original_run)

            copied_runs = CopiedValidations.objects.all()
            assert len(copied_runs) == 2
            assert copied_runs[0].original_run is None

            # now I remove one of the validations
            self.delete_run(copied_run)
            # now should be 1, because copied validaitons has been removed
            copied_runs = CopiedValidations.objects.all()
            assert len(copied_runs) == 1

            # and now I'm removing the user who copied validations
            user_to_remove = self.testuser2
            user_to_remove.delete()
            copied_runs = CopiedValidations.objects.all()
            assert len(copied_runs) == 0
