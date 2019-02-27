import matplotlib.pyplot as plt
plt.switch_backend('agg') ## this allows headless graph production
import logging
from os import path
from zipfile import ZipFile

import netCDF4

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from validator.validation import globals
from validator.validation.globals import METRICS


__logger = logging.getLogger(__name__)

def generate_graph(validation_run, outfolder, variable, label):
    if not validation_run.output_file:
        return None

    filename = path.join(outfolder, 'boxplot_{}.png'.format(variable))

    with netCDF4.Dataset(validation_run.output_file.path) as ds:
        values = ds.variables[variable][:]

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

    plt.savefig(filename)
    plt.clf()

    return filename

def generate_overview_map(validation_run, outfolder):
    if not validation_run.output_file:
        return None

    filename = path.join(outfolder, 'overview.png')

    with netCDF4.Dataset(validation_run.output_file.path) as ds:
        values = ds.variables['R'][:]
        lats = ds.variables['lat'][:]
        lons = ds.variables['lon'][:]

    ax = plt.axes(projection=ccrs.PlateCarree())
    cm = plt.cm.get_cmap('RdYlBu')

    the_plot = None

    # do scatter plot for ISMN and heatmap for everything else
    if(validation_run.ref_dataset.short_name == globals.ISMN):
        the_plot = plt.scatter(lons, lats, c=values, cmap=cm, s=3, vmin=-1.0, vmax=1.0)

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
        the_plot = plt.imshow(values_alt, cmap=cm, interpolation='none', extent=extent, vmin=-1.0, vmax=1.0)

    plt.colorbar(the_plot, orientation='horizontal', label="Pearson's r", pad=0.05)

    plt.title("Pearson's r")
    ax.coastlines()
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)

    plt.tight_layout()
    plt.savefig(filename,bbox_inches = 'tight', pad_inches = 0.1, dpi=200)
    plt.clf()
    return filename

def generate_all_graphs(validation_run, outfolder):
    zipfilename = path.join(outfolder, 'graphs.zip')
    __logger.debug('Trying to create zipfile {}'.format(zipfilename))
    with ZipFile(zipfilename, 'w') as myzip:
        for metric in METRICS:
            fn = generate_graph(validation_run, outfolder, metric, METRICS[metric])
            arcname = path.basename(fn)
            myzip.write(fn, arcname=arcname)
        fn=generate_overview_map(validation_run, outfolder)
        arcname = path.basename(fn)
        myzip.write(fn, arcname=arcname)
