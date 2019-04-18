import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
# plt.switch_backend('agg') ## this allows headless graph production
import logging
from os import path, remove
from zipfile import ZipFile, ZIP_DEFLATED
import netCDF4
import seaborn as sns
import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import numpy as np
from validator.validation import globals
from validator.validation.globals import METRICS


__logger = logging.getLogger(__name__)

_metric_value_ranges = {
    'R': [-1, 1],
    'p_R': [0, 1],
    'rho': [-1, 1],
    'p_rho': [0, 1],
    'RMSD': [0, None],
    'BIAS': [None, None],
    'n_obs': [0, None],
    'urmsd': [0, None],
    'RSS': [0, None],
}

# label format for all metrics
_metric_description = {
    'R': '',
    'p_R': '',
    'rho': '',
    'p_rho': '',
    'RMSD': r' in ${}$',
    'BIAS': r' in ${}$',
    'n_obs': '',
    'urmsd': r' in ${}$',
    'RSS': r' in $({})^2$',
}

# units for all datasets
_metric_units = {
    'ISMN': r'm^3 m^{-3}',
    'C3S': r'm^3 m^{-3}',
    'GLDAS': r'm^3 m^{-3}',
    'ASCAT': r'percentage of saturation',
    'SMAP': r'm^3 m^{-3}'
}

# colormaps used for plotting metrics
_colormaps = {
    'R': 'RdYlBu',
    'p_R': 'RdYlBu_r',
    'rho': 'RdYlBu',
    'p_rho': 'RdYlBu_r',
    'RMSD': 'RdYlBu_r',
    'BIAS': 'coolwarm',
    'n_obs': 'RdYlBu',
    'urmsd': 'RdYlBu_r',
    'RSS': 'RdYlBu_r',
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

    plt.title('Validation {} ({}) vs {} ({})'.format(
        validation_run.data_dataset.pretty_name,
        validation_run.data_version.pretty_name,
        validation_run.ref_dataset.pretty_name,
        validation_run.ref_version.pretty_name))
    plt.ylabel(label + _metric_description[variable].format(_metric_units[unit_ref]))
    plt.text(-0.14, -0.14, u'\u00A9 QA4SM (www.qa4sm.eodc.eu)', fontsize=10, color='black',
             ha='left', va='bottom', alpha=0.5, transform=ax.transAxes)
    plt.tight_layout()
    plt.savefig(png_filename, bbox_inches='tight', pad_inches=0.1,)
    plt.savefig(svg_filename, bbox_inches='tight', pad_inches=0.1,)
    plt.close()
    return [png_filename, svg_filename]


def generate_overview_map(validation_run, outfolder, variable, label, values, unit_ref):
    png_filename = path.join(outfolder, 'overview_{}.png'.format(variable))
    svg_filename = path.join(outfolder, 'overview_{}.svg'.format(variable))

    with netCDF4.Dataset(validation_run.output_file.path) as ds:
        lats = ds.variables['lat'][:]
        lons = ds.variables['lon'][:]

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
    if validation_run.ref_dataset.short_name == globals.ISMN:
        # change size of markers dependent on zoom level
        markersize = 1.5 * (360 / lon_interval)
        the_plot = plt.scatter(lons, lats, c=values, cmap=cm, s=markersize, vmin=v_min, vmax=v_max,
                               edgecolors='black', linewidths=0.05, zorder=3)
    else:
        ax.set_extent(extent, crs=data_crs)
        lons, lats = np.meshgrid(lons, lats)
        the_plot = ax.pcolormesh(lons, lats, values, cmap=cm, transform=data_crs, vmin=v_min, vmax=v_max)

    plt.title('Validation {} ({}) vs {} ({})'.format(
        validation_run.data_dataset.pretty_name,
        validation_run.data_version.pretty_name,
        validation_run.ref_dataset.pretty_name,
        validation_run.ref_version.pretty_name), fontsize=8)
    ax.coastlines(linewidth=0.2, zorder=2)
    ax.add_feature(cfeature.STATES, linewidth=0.05, zorder=2)
    ax.add_feature(cfeature.BORDERS, linewidth=0.1, zorder=2)
    ax.add_feature(cfeature.LAND, color='white', zorder=0)
    ax.text(0, -0.30, u'\u00A9 QA4SM (www.qa4sm.eodc.eu)', fontsize=5,
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

    # plt.tight_layout()
    plt.savefig(png_filename, bbox_inches='tight', pad_inches=0.1, dpi=300)
    plt.savefig(svg_filename, bbox_inches='tight', pad_inches=0.1, dpi=300)
    plt.close()

    return [png_filename, svg_filename]


def generate_all_graphs(validation_run, outfolder):
    if not validation_run.output_file:
        return None

    zipfilename = path.join(outfolder, 'graphs.zip')
    __logger.debug('Trying to create zipfile {}'.format(zipfilename))

    # get units for plot labels
    if validation_run.scaling_ref == 'data':
        unit_ref = validation_run.data_dataset.short_name
    else:
        unit_ref = validation_run.ref_dataset.short_name

    with ZipFile(zipfilename, 'w', ZIP_DEFLATED) as myzip:
        for metric in METRICS:
            print(metric)
            values = pd.DataFrame()
            data = None
            with netCDF4.Dataset(validation_run.output_file.path) as ds:
                items = [i for i in ds.variables.keys() if i.split('__')[0] == metric]
                for i in items:
                    data = ds.variables[i][:]
                    try:
                        values[i.split('__')[1]] = data.compressed()
                    except:
                        # e.g. n_obs
                        values[i] = data.compressed()

                if data is not None:
                    file1, file2 = generate_overview_map(validation_run, outfolder, metric, METRICS[metric], data,
                                                         unit_ref)
                    arcname = path.basename(file1)
                    myzip.write(file1, arcname=arcname)
                    arcname = path.basename(file2)
                    myzip.write(file2, arcname=arcname)
                    remove(file2)  # we don't need the vector image anywhere but in the zip

            if not values.empty:
                file1, file2 = generate_boxplot(validation_run, outfolder, metric, METRICS[metric], values, unit_ref)
                arcname = path.basename(file1)
                myzip.write(file1, arcname=arcname)
                arcname = path.basename(file2)
                myzip.write(file2, arcname=arcname)
                remove(file2)  # we don't need the vector image anywhere but in the zip