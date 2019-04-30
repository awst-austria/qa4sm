import matplotlib.pyplot as plt
from validator.models.dataset_configuration import DatasetConfiguration
plt.switch_backend('agg') ## this allows headless graph production
import matplotlib.ticker as mticker

import logging
from os import path, remove
from zipfile import ZipFile, ZIP_DEFLATED

from re import search as regex_search
from re import match as regex_match
from re import IGNORECASE

import netCDF4
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import seaborn as sns

from validator.validation import globals
from validator.validation.globals import METRICS


__logger = logging.getLogger(__name__)

_metric_value_ranges = {
    'R': [-1, 1],
    'p_R': [0, 1],
    'rho': [-1, 1],
    'p_rho': [0, 1],
    'rmsd': [0, None],
    'bias': [None, None],
    'n_obs': [0, None],
    'ubRMSD': [0, None],
    'RSS': [0, None],
    'mse' : [None, None],
    'mse_corr' : [None, None],
    'mse_bias' : [None, None],
    'mse_var' : [None, None],
}

# label format for all metrics
_metric_description = {
    'R': '',
    'p_R': '',
    'rho': '',
    'p_rho': '',
    'rmsd': r' in ${}$',
    'bias': r' in ${}$',
    'n_obs': '',
    'ubRMSD': r' in ${}$',
    'RSS': r' in $({})^2$',
    'mse' : '',
    'mse_corr' : '',
    'mse_bias' : '',
    'mse_var' : '',
}

# colormaps used for plotting metrics
_colormaps = {
    'R': 'RdYlBu',
    'p_R': 'RdYlBu_r',
    'rho': 'RdYlBu',
    'p_rho': 'RdYlBu_r',
    'rmsd': 'RdYlBu_r',
    'bias': 'coolwarm',
    'n_obs': 'RdYlBu',
    'ubRMSD': 'RdYlBu_r',
    'RSS': 'RdYlBu_r',
    'mse' : 'RdYlBu_r',
    'mse_corr' : 'RdYlBu_r',
    'mse_bias' : 'RdYlBu_r',
    'mse_var' : 'RdYlBu_r',
}

# units for all datasets
_metric_units = {
    'ISMN': r'm^3 m^{-3}',
    'C3S': r'm^3 m^{-3}',
    'GLDAS': r'm^3 m^{-3}',
    'ASCAT': r'percentage of saturation',
    'SMAP': r'm^3 m^{-3}'
}

def generate_boxplot(validation_run, outfolder, variable, label, values, unit_ref):
    png_filename = path.join(outfolder, 'boxplot_{}.png'.format(variable))
    svg_filename = path.join(outfolder, 'boxplot_{}.svg'.format(variable))

    values = values.melt(value_vars=values.columns, var_name='Validation')

    # use seaborn library for boxplot
    sns.set_style("whitegrid")
    ax = sns.boxplot(data=values, x='Validation', y='value', width=0.15, showfliers=False, color='white')
    sns.despine()
    ax.set_ylim(_metric_value_ranges[variable])

    plot_title="Validation " + " vs ".join(
        ['{} ({})'.format(dc.dataset.pretty_name, dc.version.pretty_name) for dc in validation_run.dataset_configurations.all()])

    plt.title(plot_title)
    plt.ylabel(label + _metric_description[variable].format(_metric_units[unit_ref]))
    plt.text(-0.14, -0.14, u'made with QA4SM (www.qa4sm.eodc.eu)', fontsize=10, color='black',
             ha='left', va='bottom', alpha=0.5, transform=ax.transAxes)
    plt.tight_layout()
    plt.savefig(png_filename, bbox_inches='tight', pad_inches=0.1,)
    plt.savefig(svg_filename, bbox_inches='tight', pad_inches=0.1,)
    plt.close()
    return [png_filename, svg_filename]


def generate_overview_map(validation_run, outfolder, variable, label, values, dc1, dc2, pair_name, unit_ref, lons, lats):
    png_filename = path.join(outfolder, 'overview_{}_{}.png'.format(pair_name, variable))
    svg_filename = path.join(outfolder, 'overview_{}_{}.svg'.format(pair_name, variable))

    data_crs = ccrs.PlateCarree()
    ax = plt.axes(projection=data_crs)
    cm = plt.cm.get_cmap(_colormaps[variable])
    ax.outline_patch.set_linewidth(0.2)

    v_min = _metric_value_ranges[variable][0]
    v_max = _metric_value_ranges[variable][1]

    padding = 5
    extent = [lons.min()-padding, lons.max()+padding, lats.min()-padding, lats.max()+padding]
    lon_interval = extent[1] - extent[0]
    lat_interval = extent[3] - extent[2]

    # do scatter plot for ISMN and heatmap for everything else
    if validation_run.reference_configuration.dataset.short_name == globals.ISMN:
        # change size of markers dependent on zoom level
        markersize = 1.5 * (360 / lon_interval)
        the_plot = plt.scatter(lons, lats, c=values, cmap=cm, s=markersize, vmin=v_min, vmax=v_max,
                               edgecolors='black', linewidths=0.05, zorder=3)
    else:
        lats_map = np.arange(extent[3], extent[2], -0.25)
        lons_map = np.arange(extent[0], extent[1], 0.25)
#         lats_map = np.arange(89.875, -60, -0.25)
#         lons_map = np.arange(-179.875, 180, 0.25)
        values_map = np.empty((len(lats_map), len(lons_map)))
        values_map[:] = np.nan

        for i in range(0, len(values)):
            values_map[np.where(lats_map == lats[i])[0][0]][np.where(lons_map == lons[i])[0][0]] = values[i]

#         extent = [-179.875, 179.875, -59.875, 89.875]
        the_plot = plt.imshow(values_map, cmap=cm, interpolation='none', extent=extent,
                              vmin=v_min, vmax=v_max, zorder=1)

    plot_title="Validation {} ({}) vs {} ({})".format(
        dc1.dataset.short_name, dc1.version.short_name, dc2.dataset.short_name, dc2.version.short_name)

    plt.title(plot_title,fontsize=8)
    ax.coastlines(linewidth=0.2, zorder=2)
    ax.add_feature(cfeature.STATES, linewidth=0.05, zorder=2)
    ax.add_feature(cfeature.BORDERS, linewidth=0.1, zorder=2)
    ax.add_feature(cfeature.LAND, color='white', zorder=0)
    ax.text(0, -0.40, u'made with QA4SM (www.qa4sm.eodc.eu)', fontsize=5,
            color='black', ha='left', va='bottom', alpha=0.5, transform=ax.transAxes)

    # add gridlines
    grid_interval_lon = 5 * round((lon_interval/3) / 5)
    grid_interval_lat = 5 * round((lat_interval/3) / 5)
    if grid_interval_lat > 30:
        grid_interval_lat = 30
    if grid_interval_lon > 30:
        grid_interval_lon = 30
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.2, color='gray', alpha=0.5, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_left = False
    gl.xlocator = mticker.FixedLocator(np.arange(-180, 181, grid_interval_lon))
    gl.ylocator = mticker.FixedLocator(np.arange(-90, 91, grid_interval_lat))
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 4, 'color': 'black'}
    gl.ylabel_style = {'size': 4, 'color': 'black'}

    # add colorbar
    cbar = plt.colorbar(the_plot, orientation='horizontal', pad=0.05)
    cbar.set_label(label + _metric_description[variable].format(_metric_units[unit_ref]), size=5)
    cbar.outline.set_linewidth(0.2)
    cbar.outline.set_edgecolor('black')
    cbar.ax.tick_params(width=0.2, labelsize=4)

#     plt.tight_layout()
    plt.savefig(png_filename, bbox_inches='tight', pad_inches=0.1, dpi=200)
    plt.savefig(svg_filename, bbox_inches='tight', pad_inches=0.1, dpi=200)
    plt.close()

    return [png_filename, svg_filename]

def identify_dataset_configs(validation_run, metric_col_name):
    ds_match = regex_match(r'.*_between_(([0-9]+)-(.*)_([0-9]+)-(.*))', metric_col_name)
    if ds_match:
        pair_name = ds_match.group(1)
        dc1_num = int(ds_match.group(2))
        ds1_name = ds_match.group(3)
        dc2_num = int(ds_match.group(4))
        ds2_name = ds_match.group(5)

        ds_order = validation_run.get_datasetconfiguration_order()
        dc1 = DatasetConfiguration.objects.get(pk = ds_order[dc1_num - 1])
        dc2 = DatasetConfiguration.objects.get(pk = ds_order[dc2_num - 1])

        if ((dc1.dataset.short_name != ds1_name) or (dc2.dataset.short_name != ds2_name)):
            raise Exception('Can\'t figure out correct dataset configuration')

    else: # in case we still have an old netcdf file? TODO: remove this
        dc1 = validation_run.dataset_configurations.first()
        dc2 = validation_run.dataset_configurations.last()
        pair_name = '1-{}_2-{}'.format(dc1.dataset.short_name, dc2.dataset.short_name)

    return [dc1, dc2, pair_name]

def generate_all_graphs(validation_run, outfolder):
    if not validation_run.output_file:
        return None

    zipfilename = path.join(outfolder, 'graphs.zip')
    __logger.debug('Trying to create zipfile {}'.format(zipfilename))

    # get units for plot labels

    unit_ref = validation_run.reference_configuration.dataset.short_name

    with ZipFile(zipfilename, 'w', ZIP_DEFLATED) as myzip:
        with netCDF4.Dataset(validation_run.output_file.path) as ds:
            lats = ds.variables['lat'][:]
            lons = ds.variables['lon'][:]

            for metric in METRICS:
                ## get all 'columns' (dataset-pair results) from the netcdf file that start with the current metric name
                cur_metric_cols = ds.get_variables_by_attributes(name=lambda v: regex_search(r'^{}(_between|$)'.format(metric), v, IGNORECASE) is not None)

                metric_table = pd.DataFrame()
                for metric_col in cur_metric_cols:
                    ## figure out dataset configurations for current pair
                    dc1, dc2, pair_name = identify_dataset_configs(validation_run, metric_col.name)

                    ## build table for current metric, one column per dataset-pair
                    metric_table[pair_name] = metric_col[:].compressed()

                    ## TODO: currently, overview maps are overwritten

                    ## make maps for all columns
                    if metric_col[:] is not None:
                        file1, file2 = generate_overview_map(validation_run, outfolder, metric, METRICS[metric], metric_col[:], dc1, dc2, pair_name, unit_ref, lons, lats)
                        arcname = path.basename(file1)
                        myzip.write(file1, arcname=arcname)
                        arcname = path.basename(file2)
                        myzip.write(file2, arcname=arcname)
                        remove(file2)  # we don't need the vector image anywhere but in the zip

                ## make boxplot graph with boxplots for all columns
                if not metric_table.empty:
                    file1, file2 = generate_boxplot(validation_run, outfolder, metric, METRICS[metric], metric_table, unit_ref)
                    arcname = path.basename(file1)
                    myzip.write(file1, arcname=arcname)
                    arcname = path.basename(file2)
                    myzip.write(file2, arcname=arcname)
                    remove(file2)  # we don't need the vector image anywhere but in the zip
