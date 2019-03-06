import matplotlib.pyplot as plt
plt.switch_backend('agg') ## this allows headless graph production
import logging
from os import path, remove
from zipfile import ZipFile, ZIP_DEFLATED

import netCDF4

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from validator.validation import globals
from validator.validation.globals import METRICS


__logger = logging.getLogger(__name__)

_metric_value_ranges = {
    'R' : [-1, 1],
    'p_R' : [0, 1],
    'rho' : [-1, 1],
    'p_rho' : [0, 1],
    'RMSD' : [0, None],
    'BIAS' : [None, None],
    'n_obs' : [0, None],
    'urmsd' : [0, None],
    'RSS' : [0, None],
    }


def generate_boxplot(validation_run, outfolder, variable, label, values):
    if not validation_run.output_file:
        return None

    png_filename = path.join(outfolder, 'boxplot_{}.png'.format(variable))
    svg_filename = path.join(outfolder, 'boxplot_{}.svg'.format(variable))

    values = [x for x in values if (np.isnan(x) != True)]

    plt.boxplot(values, sym='+')
    plt.ylabel(label)
    plt.title('Validation {} ({}) vs {} ({})'.format(
        validation_run.data_dataset.pretty_name,
        validation_run.data_version.pretty_name,
        validation_run.ref_dataset.pretty_name,
        validation_run.ref_version.pretty_name))
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    plt.tight_layout()

    plt.savefig(png_filename)
    plt.savefig(svg_filename)
    plt.clf()

    return [png_filename, svg_filename]

def generate_overview_map(validation_run, outfolder, variable, label, values):
    if not validation_run.output_file:
        return None

    png_filename = path.join(outfolder, 'overview_{}.png'.format(variable))
    svg_filename = path.join(outfolder, 'overview_{}.svg'.format(variable))

    with netCDF4.Dataset(validation_run.output_file.path) as ds:
        lats = ds.variables['lat'][:]
        lons = ds.variables['lon'][:]

    ax = plt.axes(projection=ccrs.PlateCarree())
    cm = plt.cm.get_cmap('RdYlBu')

    the_plot = None

    v_min = _metric_value_ranges[variable][0]
    v_max = _metric_value_ranges[variable][1]

    # do scatter plot for ISMN and heatmap for everything else
    if(validation_run.ref_dataset.short_name == globals.ISMN):
        the_plot = plt.scatter(lons, lats, c=values, cmap=cm, s=3, vmin=v_min, vmax=v_max)

    else:
        values_alt = np.empty((720, 1440,))
        values_alt[:] = np.nan
        lats_alt = np.linspace(90, -90, 720)
        lons_alt = np.linspace(-180, 180, 1440)

        for i in range(0, len(values)):
            nearest_lon_idx = (np.abs(lons_alt - lons[i]).argmin())
            nearest_lat_idx = (np.abs(lats_alt - lats[i]).argmin())
            values_alt[nearest_lat_idx][nearest_lon_idx] = values[i]

        extent = [-180.0, 180.0, -90.0, 90.0]
        the_plot = plt.imshow(values_alt, cmap=cm, interpolation='none', extent=extent, vmin=v_min, vmax=v_max)

    plt.colorbar(the_plot, orientation='horizontal', label=label, pad=0.05)

    plt.title('Validation {} ({}) vs {} ({})'.format(
        validation_run.data_dataset.pretty_name,
        validation_run.data_version.pretty_name,
        validation_run.ref_dataset.pretty_name,
        validation_run.ref_version.pretty_name))
    ax.coastlines()
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)

    plt.tight_layout()
    plt.savefig(png_filename, bbox_inches = 'tight', pad_inches = 0.1, dpi=200)
    plt.savefig(svg_filename, bbox_inches = 'tight', pad_inches = 0.1, dpi=200)
    plt.clf()
    return [png_filename, svg_filename]

def generate_all_graphs(validation_run, outfolder):
    zipfilename = path.join(outfolder, 'graphs.zip')
    __logger.debug('Trying to create zipfile {}'.format(zipfilename))
    with ZipFile(zipfilename, 'w', ZIP_DEFLATED) as myzip:
        for metric in METRICS:
            with netCDF4.Dataset(validation_run.output_file.path) as ds:
                values = ds.variables[metric][:]

            file1, file2 = generate_boxplot(validation_run, outfolder, metric, METRICS[metric], values)
            arcname = path.basename(file1)
            myzip.write(file1, arcname=arcname)
            arcname = path.basename(file2)
            myzip.write(file2, arcname=arcname)
            remove(file2) # we don't need the vector image anywhere but in the zip

            file1, file2 = generate_overview_map(validation_run, outfolder, metric, METRICS[metric], values)
            arcname = path.basename(file1)
            myzip.write(file1, arcname=arcname)
            arcname = path.basename(file2)
            myzip.write(file2, arcname=arcname)
            remove(file2) # we don't need the vector image anywhere but in the zip
