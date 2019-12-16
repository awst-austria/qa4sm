import matplotlib.pyplot as plt
plt.switch_backend('agg') ## this allows headless graph production
import logging
from os import path, remove
from zipfile import ZipFile, ZIP_DEFLATED

from valentina.settings import BASE_DIR

from cartopy import config as cconfig
cconfig['data_dir'] = path.join(BASE_DIR, 'cartopy')

import os
from qa4sm_reader.plot_all import plot_all


__logger = logging.getLogger(__name__)



def generate_all_graphs(validation_run, outfolder):
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
            os.remove(svgfile)


def get_dataset_pairs(validation_run):
    pairs = []

    ref = None
    datasets = []
    for ds_num, dataset_config in enumerate(validation_run.dataset_configurations.all(), start=1):
        dataset_name = '{}-{}'.format(ds_num, dataset_config.dataset.short_name)
        if(dataset_config.id == validation_run.reference_configuration.id):
            ref = dataset_name
        else:
            datasets.append(dataset_name)

    for ds in datasets:
        pair = '{}_and_{}'.format(ref, ds)
        pairs.append(pair)

    return pairs
