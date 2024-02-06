#%%
import warnings

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
plt.switch_backend('agg')  ## this allows headless graph production

import logging
from os import path, remove
from zipfile import ZipFile, ZIP_DEFLATED

import sys
sys.path.append('/home/nbader/Documents/QA4SM_tasks/jira-744/qa4sm-reader/src/')
from qa4sm_reader.plot_all import plot_all, get_img_stats
from qa4sm_reader.comparing import QA4SMComparison, ComparisonError, SpatialExtentError

from django.conf import settings

from cartopy import config as cconfig

# cconfig['data_dir'] = path.join(settings.BASE_DIR, 'cartopy')

# from validator.validation.globals import OUTPUT_FOLDER, METRICS, METRIC_TEMPLATE, TC_METRICS, TC_METRIC_TEMPLATE
import os
from io import BytesIO
import base64
from parse import parse

__logger = logging.getLogger(__name__)

def generate_all_graphs(validation_run, temporal_sub_windows: np.ndarray, outfolder: str, save_metadata='threshold'):
    """
    Create all default graphs for validation run. This is done
    using the qa4sm-reader plotting library.

    Parameters
    ----------
    validation_run : ValidationRun
        The validation run to make plots for.
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

    fnb, fnm, fcsv = plot_all(
        validation_run.output_file.path,
        temporal_sub_windows=temporal_sub_windows,
        out_dir=outfolder,
        out_type='png',
        save_metadata=save_metadata
    )
    fnb_svg, fnm_svg, fcsv = plot_all(
        validation_run.output_file.path,
        temporal_sub_windows=temporal_sub_windows,
        out_dir=outfolder,
        out_type='svg',
        save_metadata=save_metadata
    )

    with ZipFile(zipfilename, 'w', ZIP_DEFLATED) as myzip:
        for pngfile in fnb + fnm:
            arcname = path.basename(pngfile)
            myzip.write(pngfile, arcname=arcname)
        for svgfile in fnb_svg + fnm_svg:
            arcname = path.basename(svgfile)
            myzip.write(svgfile, arcname=arcname)
            remove(svgfile)


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
    pairs, triples = {}, {}
    ref0_config = None

    metrics = {}

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

                template = ''.join([METRIC_TEMPLATE[0],
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

                template = ''.join([TC_METRIC_TEMPLATE[0],
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

#%%
if __name__ == '__main__':
    dirpath = '/home/nbader/Documents/QA4SM_tasks/jira-744/qa4sm/output/381f63ce-2078-4615-9b8a-fdf1170e6bd0_c'
    fnb, fnm, fcsv = plot_all(
    filepath=os.path.join(dirpath, '0-ISMN.soil_moisture_with_1-C3S_combined.sm.nc'),
    out_dir=os.path.join(dirpath, 'graphs'),
    out_type='png',
    save_metadata='threshold'
    )

# %%
