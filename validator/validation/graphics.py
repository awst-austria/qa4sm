import matplotlib.pyplot as plt
plt.switch_backend('agg') ## this allows headless graph production

import logging
from os import path, remove
from zipfile import ZipFile, ZIP_DEFLATED

from qa4sm_reader.plot_all import plot_all

from django.conf import settings

from cartopy import config as cconfig
cconfig['data_dir'] = path.join(settings.BASE_DIR, 'cartopy')

from validator.validation.globals import OUTPUT_FOLDER, METRICS, TC_METRICS, METRIC_TEMPLATE, TC_METRIC_TEMPLATE
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


    fnb, fnm = plot_all(validation_run.output_file.path,
        out_dir=outfolder, out_type='png')
    fnb_svg, fnm_svg = plot_all(validation_run.output_file.path,
        out_dir=outfolder, out_type='svg')


    with ZipFile(zipfilename, 'w', ZIP_DEFLATED) as myzip:
        for pngfile in fnb + fnm:
            print(pngfile)
            arcname = path.basename(pngfile)
            myzip.write(pngfile, arcname=arcname)
        for svgfile in fnb_svg + fnm_svg:
            print(svgfile)
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
    pairs : list
        Dataset pairs to show in the dropdown
    triples : list
        Dataset triples to show in the dropdown
    metrics : dict
        All metrics that are found
    ref0_config : bool or None
        True if the ref has id 0 (sorted ids).
    """

    run_dir = path.join(OUTPUT_FOLDER, str(validation_run.id))
    pairs, triples = [] ,[]
    ref0_config = None

    ds_names = [ds_config.dataset.short_name for ds_config in validation_run.dataset_configurations.all()]

    metrics = {}

    for root, dirs, files in os.walk(run_dir):
        for f in files:
            if not f.endswith('.png'): continue

            for pair_metric in METRICS.keys():

                template = ''.join([METRIC_TEMPLATE[0],
                                    METRIC_TEMPLATE[1].format(metric=pair_metric)]) + '.png'

                parsed = parse(template,f)
                if parsed is None:
                    continue
                else:
                    if (parsed['ds_ref'] in ds_names) and (parsed['ds_sat'] in ds_names):
                        ref = f"{parsed['id_ref']}-{parsed['ds_ref']}"
                        ds = f"{parsed['id_sat']}-{parsed['ds_sat']}"

                        if ref0_config is None and (int(parsed['id_ref']) == 0):
                            ref0_config = True

                        if pair_metric not in metrics.keys():
                            metrics[pair_metric] = METRICS[pair_metric]

                        pair = '{}_and_{}'.format(ref, ds)
                        if pair not in pairs:
                            pairs.append(pair)

            for tcol_metric in TC_METRICS.keys():

                template = ''.join([TC_METRIC_TEMPLATE[0],
                                    TC_METRIC_TEMPLATE[1].format(metric=tcol_metric),
                                    TC_METRIC_TEMPLATE[2]]) + '.png'

                parsed = parse(template, f)
                if parsed is None:
                    continue
                else:
                    if all([parsed[d] in ds_names for d in ['ds_ref', 'ds_sat', 'ds_sat2', 'ds_met']]):
                        ref = f"{parsed['id_ref']}-{parsed['ds_ref']}"
                        ds = f"{parsed['id_sat']}-{parsed['ds_sat']}"
                        ds2 = f"{parsed['id_sat2']}-{parsed['ds_sat2']}"
                        ds_met = f"{parsed['id_met']}-{parsed['ds_met']}"

                        metric = f"{tcol_metric}_for_{ds_met}"

                        if metric not in metrics.keys():
                            metrics[metric] = f"{TC_METRICS[tcol_metric]} for {ds_met}"

                        triple = '{}_and_{}_and_{}'.format(ref, ds, ds2)

                        if triple not in triples:
                            triples.append(triple)
    # import logging
    # __logger = logging.getLogger(__name__)
    # __logger.debug(f"Pairs: {pairs}")
    # __logger.debug(f"Triples: {triples}")
    # __logger.debug(f"Metrics: {metrics}")

    return pairs, triples, metrics, ref0_config