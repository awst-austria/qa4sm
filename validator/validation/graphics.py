import warnings

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
plt.switch_backend('agg')  ## this allows headless graph production

import logging
from os import path, remove
from shutil import rmtree
from zipfile import ZipFile, ZIP_DEFLATED

from qa4sm_reader.plot_all import plot_all, get_img_stats
from qa4sm_reader.comparing import QA4SMComparison, ComparisonError, SpatialExtentError

from django.conf import settings

from cartopy import config as cconfig
from typing import List, Tuple, Dict, Set
from pathlib import PosixPath

cconfig['data_dir'] = path.join(settings.BASE_DIR, 'cartopy')

from validator.validation.globals import OUTPUT_FOLDER, METRICS as READER_METRICS, METRIC_TEMPLATE, TC_METRICS, \
    TC_METRIC_TEMPLATE, DEFAULT_TSW, STABILITY_METRICS
import os
from io import BytesIO
import base64
from parse import parse

__logger = logging.getLogger(__name__)

def generate_all_graphs(validation_run, temporal_sub_windows: List[str], outfolder: str, save_metadata='threshold'):
    """
    Create all default graphs for validation run. This is done
    using the qa4sm-reader plotting library.

    Parameters
    ----------
    validation_run : ValidationRun
        The validation run to make plots for.
    temporal_sub_windows: List[str]
        Temporal sub windows to plot.
    outfolder : str
        Directoy where graphs are stored.
    save_metadata: str, optional (default: 'threshold')
        'threshold' will only create box plots if there are enough observations
        'all' will create all plots, even if there are not enough observations
        'never' will never create box plots
    """
    if not validation_run.output_file:
        return None

    zipfilename = path.join(outfolder, 'graphs.zip')
    __logger.debug('Trying to create zipfile {}'.format(zipfilename))

    fnb, fnm, fcsv, fncb, _ = plot_all(
        validation_run.output_file.path,
        temporal_sub_windows=temporal_sub_windows,
        out_dir=outfolder,
        out_type=['png', 'svg'],
        save_metadata=save_metadata
    )

    plot_all_output_dict = sort_filenames_to_filetypes((fnb, fnm, fcsv, fncb))
    flattened_list = [item for inner_dict in plot_all_output_dict.values() for lst in inner_dict.values() for item in lst]
    root_dir = os.path.dirname(os.path.commonprefix(flattened_list))

    with ZipFile(zipfilename, 'w', ZIP_DEFLATED) as myzip:
        pngfiles = files_to_zip(plot_all_output_dict, 'png')
        svgfiles = files_to_zip(plot_all_output_dict, 'svg')

        for pngfile in pngfiles:
            arcname = os.path.relpath(pngfile, root_dir)
            myzip.write(pngfile, arcname=arcname)

        for svgfile in svgfiles:
            arcname = os.path.relpath(svgfile, root_dir)
            myzip.write(svgfile, arcname=arcname)
            remove(svgfile)

    collect_statitics_files(dir=outfolder)

    clean_output_folder(dir=outfolder,
                        to_be_deleted=[x for x in temporal_sub_windows if x != DEFAULT_TSW])


def get_dataset_combis_and_metrics_from_files(validation_run):
    """
    Go through plots of validation run and detect the dataset names and ids.
    Create combinations of id-REF_and_id-SAT to show the plots on the results
    page.

    Parameters
    ----------
    validation_run
        Validation run object

    Returns
    -------
    pairs : dict
        Dataset pairs and pretty names to show in the dropdown
    triples : dict
        Dataset triples and pretty names to show in the dropdown
    metrics : dict
        All metrics that are found
    ref0_config : bool or None
        True if the ref has id 0 (sorted ids).
    """

    run_dir = path.join(OUTPUT_FOLDER, str(validation_run.id))
    metric_template = METRIC_TEMPLATE[0]

    if "bulk" in os.listdir(run_dir):
        run_dir += '/bulk'
        metric_template = 'bulk_' + metric_template

    pairs, triples = {}, {}
    ref0_config = None

    metrics = {}
    bulk_prefix = ''
    if "bulk" in run_dir:
        bulk_prefix += 'bulk_'

    if validation_run.stability_metrics:
        METRICS = {**READER_METRICS, **STABILITY_METRICS}
    else:
        METRICS = READER_METRICS

    # if validation_run
    for root, dirs, files in os.walk(run_dir):
        for f in files:
            if not f.endswith('.png'): continue

            for pair_metric in METRICS.keys():

                if pair_metric == 'n_obs':
                    metrics['n_obs'] = METRICS['n_obs']
                    continue

                if pair_metric == 'status':
                    metrics['status'] = METRICS['status']
                    continue

                template = ''.join([metric_template,
                                    METRIC_TEMPLATE[1].format(metric=pair_metric)]) + '.png'
                parsed = parse(template, f)

                if parsed is None:
                    continue
                else:
                    ref = f"{parsed['id_ref']}-{parsed['ds_ref']}"
                    ds = f"{parsed['id_sat']}-{parsed['ds_sat']}"

                    if ref0_config is None and (int(parsed['id_ref']) == 0):
                        ref0_config = True

                    if pair_metric not in metrics.keys():
                        metrics[pair_metric] = METRICS[pair_metric]

                    pair = '{}_and_{}'.format(ref, ds)
                    pretty_pair = '{} and {}'.format(ref, ds)
                    if pair not in pairs.keys():
                        pairs[pair] = pretty_pair  # pretty name

            for tcol_metric in TC_METRICS.keys():
                template = bulk_prefix + ''.join([TC_METRIC_TEMPLATE[0],
                                                  TC_METRIC_TEMPLATE[1].format(metric=tcol_metric),
                                                  TC_METRIC_TEMPLATE[2]]) + '.png'

                parsed = parse(template, f)
                if parsed is None:
                    continue
                else:
                    ref = f"{parsed['id_ref']}-{parsed['ds_ref']}"
                    ds = f"{parsed['id_sat']}-{parsed['ds_sat']}"
                    ds2 = f"{parsed['id_sat2']}-{parsed['ds_sat2']}"
                    ds_met = f"{parsed['id_met']}-{parsed['ds_met']}"

                    metric = f"{tcol_metric}_for_{ds_met}"

                    if metric not in metrics.keys():
                        metrics[metric] = f"{TC_METRICS[tcol_metric]} for {ds_met}"

                    triple = '{}_and_{}_and_{}'.format(ref, ds, ds2)
                    pretty_triple = '{} and {} and {}'.format(ref, ds, ds2)
                    if triple not in triples.keys():
                        triples[triple] = pretty_triple

    # import logging
    # __logger = logging.getLogger(__name__)
    # __logger.debug(f"Pairs: {pairs}")
    # __logger.debug(f"Triples: {triples}")
    # __logger.debug(f"Metrics: {metrics}")

    return pairs, triples, metrics, ref0_config


def get_inspection_table(validation_run):
    """
    Generate the quick inspection table with the summary statistics of the results

    Parameters
    ----------
    validation_run : ValidationRun
        The validation run to make plots for.

    Returns
    -------
    table : pd.DataFrame
        Quick inspection table of the results.
    """
    outfile = validation_run.output_file
    run_dir = path.join(OUTPUT_FOLDER, str(validation_run.id))
    if "bulk" in os.listdir(run_dir):
        run_dir += 'bulk/'
    # the first condition checks whether the outfile field has been properly
    # set, the second then whether the file really exists
    if bool(outfile) and path.exists(outfile.path):
        file_size = os.path.getsize(outfile.path)

        stats_file = None
        for root, dirs, files in os.walk(run_dir):
            for f in files:
                if not f.endswith('.csv'):
                    continue
                else:
                    stats_file = os.path.join(run_dir, f)
                    break

        # Check that .csv file was created
        if stats_file is not None:
            stats = pd.read_csv(stats_file, index_col="Metric", dtype=str)
        # Check that file size is less than 100 MB
        elif file_size > 100 * 2 ** 20:
            warnings.warn(
                f"File size of {file_size} bytes is too large to be read"
            )
            # Return string to distinguish with 'None' in first conditional statement
            return "No output"
        else:
            stats = get_img_stats(outfile.path)

        stats = stats.drop(columns="Group", errors="ignore")
        return stats

    else:
        # This happens when the output file has not been generated yet, because
        # the validation is still running. In this case the table won't be
        # rendered anyways.
        return None


def generate_comparison(
        validation_runs: list,
        extent: tuple = None,
        get_intersection: bool = True
) -> tuple:
    """Initializes a QA4SMComparison class"""
    outfiles = [validation_run.output_file for validation_run in validation_runs]
    # handle single validation or multiple validations
    if len(outfiles) == 1:
        outpaths = outfiles[0].path
    else:
        outpaths = []
        for file in outfiles:
            outpaths.append(file.path)

    comparison = QA4SMComparison(
        paths=outpaths,
        extent=extent,
        get_intersection=get_intersection
    )

    return comparison


def comparison_table(
        validation_runs: list,
        metric_list: list,
        extent: tuple = None,
        get_intersection: bool = True,
) -> pd.DataFrame:
    """
    Creates a pandas comparison table

    Parameters
    ----------
    validation_runs: list
        list of ValidationRun to be compared
    extent : tuple, optional (default: None)
        Area to subset the values for.
        (min_lon, max_lon, min_lat, max_lat)
    get_intersection: bool, default is True
        Whether to get the intersection or union of the two spatial exents
    metric_list: list
        list of metrics for the table

    Returns
    -------
    table: pd.DataFrame
        comparison table
    """
    comparison = generate_comparison(
        validation_runs=validation_runs,
        extent=extent,
        get_intersection=get_intersection
    )
    table = comparison.diff_table(metric_list)

    return table


def encoded_comparisonPlots(
        validation_runs: list,
        plot_type: str,
        metric: str,
        extent: tuple = None,
        get_intersection: bool = True,
) -> str:
    """
    Creates a plot encoding in base64 showing the comparison result for a set (2) or a single validation run
    (if contains 2 satellite datasets)

    Parameters
    ----------
    validation_runs: list
        list of ValidationRun to be compared
    extent : tuple, optional (default: None)
        Area to subset the values for.
        (min_lon, max_lon, min_lat, max_lat)
    get_intersection: bool, default is True
        Whether to get the intersection or union of the two spatial exents
    plot_type: str
        the plot type to show in the comparison page. Can be one of "table", "boxplot", "correlation",
        "mapplot" ("difference")
    metric: str
        the selected metric type

    Returns
    -------
    encoded: str
        base64 encoding of the plot image
    """
    comparison = generate_comparison(
        validation_runs=validation_runs,
        extent=extent,
        get_intersection=get_intersection
    )
    image = BytesIO()

    comparison.wrapper(
        method=plot_type,
        metric=metric
    )
    plt.savefig(image, format='png')
    encoded = base64.b64encode(image.getvalue()).decode('utf-8')

    return encoded


def get_extent_image(
        validation_runs: list,
        extent: tuple = None,
        get_intersection: bool = True,
        encoded: bool = True,
):
    """
    Creates an image encoding in base64 showing the selected comparison extent

    Parameters
    ----------
    validation_runs: list
        list of ValidationRun to be compared
    extent : tuple, optional (default: None)
        Area to subset the values for.
        (min_lon, max_lon, min_lat, max_lat)
    get_intersection: bool, default is True
        Whether to get the intersection or union of the two spatial exents
    encoded: bool, default is True
        Whether to encode the image that is returned

    Returns
    -------
    encoded: str
        base64 encoding of the plot image
    """
    try:
        comparison = generate_comparison(
            validation_runs=validation_runs,
            extent=extent,
            get_intersection=get_intersection
        )
    except SpatialExtentError:
        return "Raise message to check box"

    image = BytesIO()
    try:
        comparison.visualize_extent(
            intersection=get_intersection,
            plot_points=True,
        )
        plt.savefig(image, format='png')
        if encoded:
            encoded = base64.encodebytes(image.getvalue()).decode('utf-8')
            return encoded

        return image

    except ComparisonError:
        return "error encountered"


def collect_statitics_files(dir: str) -> None:
    """
    Collect all statistics files in a directory and store them in a zip file.

    Parameters
    ----------
    dir : str
        Directory to store the zip file

    Returns
    -------
    None
    """
    zipfilename = path.join(dir, 'statistics.zip')
    __logger.debug('Trying to create zipfile {}'.format(zipfilename))

    with ZipFile(zipfilename, 'w', ZIP_DEFLATED) as myzip:
        for root, dirs, files in os.walk(dir):
            for f in files:
                if f.endswith('.csv'):
                    arcname = os.path.relpath(path.join(root, f), dir)
                    myzip.write(path.join(root, f), arcname=arcname)


def clean_output_folder(dir: str, to_be_deleted: List[str]) -> None:
    """
    Clean a specified directory of given elements.

    Parameters
    ----------
    dir : str
        Directory to be cleaned
    to_be_deleted : List[str]
        List of elements (files, dirs) to be deleted

    Returns
    -------
    None
    """
    if os.path.exists(dir):
        for element in to_be_deleted:
            element_path = os.path.join(dir, element)
            if os.path.exists(element_path):
                if os.path.isfile(element_path):
                    remove(element_path)
                elif os.path.isdir(element_path):
                    rmtree(element_path)
    else:
        warnings.warn(f"Directory {dir} does not exist")


def sort_filenames_to_filetypes(plot_output: Tuple[List[PosixPath]]) -> Dict[str, Dict[str, List[PosixPath]]]:
    """
    Sorts the files, that are the output of the `qa4sm_reader.plot_all.plot_all()` into a dictionary. \
        The four keys correspond to the four lists of the `qa4sm_reader.plot_all.plot_all()` output,\
            with each values being a dictionary of the file types as key and a list of filepaths as value.


    Parameters
    ----------
    plot_output : Tuple[List[PosixPath]]
        The output of the `qa4sm_reader.plot_all.plot_all()` function

    Returns
    -------
    _out_dict : Dict[str, Dict[str, List[PosixPath]]]
        A dictionary with the four keys 'fnb', 'fnm', 'fcsv', 'fncb' and each value being a dictionary of the file \
            types as key and a list of filepaths as value.
    """

    _out_dict = {'fnb': {},
                 'fnm': {},
                 'fcsv': {},
                 'fncb': {},
                 }

    _out_dict_lut = {0: 'fnb', 1: 'fnm', 2: 'fcsv', 3: 'fncb'}

    for l, lst in enumerate(plot_output):
        lst_suffixes = list(set([el.suffix for el in lst]))
        _out_dict[_out_dict_lut[l]] = {suffix.lstrip('.'): [ffile for ffile in lst if ffile.suffix == suffix]
                                       for suffix in lst_suffixes}

    return _out_dict


def files_to_zip(plot_dict: Dict[str, Dict[str, List[PosixPath]]], filetype: str) -> Set[PosixPath]:
    """
    Collects the files of a given filetype from the plot_dict and returns them as a set.

    Parameters
    ----------
    plot_dict : Dict[str, Dict[str, List[PosixPath]]]
        The dictionary containing the filepaths of the different filetypes. \
            This should be the output of the `sort_filenames_to_filetypes()` function.
    filetype : str
        The filetype to collect the files from.

    Returns
    -------
    _files : Set[PosixPath]
        A set of the filepaths of the given filetype.
    """
    _files = plot_dict['fnb'][filetype] + plot_dict['fnm'][filetype]

    try:
        _files += plot_dict['fncb'][filetype]
    except KeyError as e:  # if there are no comparison boxplots the 'fncb' key will not be present
        warnings.warn(f"KeyError: {e}. No comparison boxplots found. Skipping...")
    finally:
        _files = set(_files)

    return _files
