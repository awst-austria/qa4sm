import matplotlib.pyplot as plt
plt.switch_backend('agg') ## this allows headless graph production

import logging
from os import path, remove
from zipfile import ZipFile, ZIP_DEFLATED

from qa4sm_reader.plot_all import plot_all

from django.conf import settings

from cartopy import config as cconfig
cconfig['data_dir'] = path.join(settings.BASE_DIR, 'cartopy')

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


def get_dataset_pairs(validation_run, ref0_config=True):
    pairs = []

    ref = None
    datasets = []

    ds_num = 1
    for dataset_config in validation_run.dataset_configurations.all():
        if ref0_config and (dataset_config.id == validation_run.reference_configuration.id):
            dataset_name = '{}-{}'.format(0, dataset_config.dataset.short_name)
            ref = dataset_name
        else:
            dataset_name = '{}-{}'.format(ds_num, dataset_config.dataset.short_name)
            if (dataset_config.id == validation_run.reference_configuration.id) and ref is None:
                ref = dataset_name
            datasets.append(dataset_name)
            ds_num = ds_num + 1


    for ds in datasets:
        pair = '{}_and_{}'.format(ref, ds)
        pairs.append(pair)

    return pairs