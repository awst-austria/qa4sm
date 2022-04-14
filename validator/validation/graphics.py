import warnings

import matplotlib.pyplot as plt
import pandas as pd

plt.switch_backend('agg')  ## this allows headless graph production

import logging
from os import path, remove
from zipfile import ZipFile, ZIP_DEFLATED

from qa4sm_reader.plot_all import plot_all, get_img_stats

from django.conf import settings

from cartopy import config as cconfig

cconfig['data_dir'] = path.join(settings.BASE_DIR, 'cartopy')

from validator.validation.globals import *
import os
from parse import *

__logger = logging.getLogger(__name__)


def generate_all_graphs(validation_run, outfolder):
    """
    Create all default graphs for validation run. This is done
    using the qa4sm-reader plotting library.

    Parameters
    ----------
    validation_run : ValidationRun
        The validation run to make plots for.
    outfolder : str
        Directoy where graphs are stored.
    """
    if not validation_run.output_file:
        return None

    zipfilename = path.join(outfolder, 'graphs.zip')
    __logger.debug('Trying to create zipfile {}'.format(zipfilename))

    fnb, fnm, fcsv = plot_all(validation_run.output_file.path,
                              out_dir=outfolder, out_type='png')
    fnb_svg, fnm_svg, fcsv = plot_all(validation_run.output_file.path,
                                      out_dir=outfolder, out_type='svg')

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
