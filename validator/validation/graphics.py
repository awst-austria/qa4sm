import matplotlib.pyplot as plt
plt.switch_backend('agg') ## this allows headless graph production
import matplotlib.ticker as mticker
import logging
from os import path, remove
from zipfile import ZipFile, ZIP_DEFLATED
import netCDF4
import seaborn as sns
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
    'BIAS': [-0.1, 0.1],
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
    'SMAP': r'm^3 m^{-3}',
    'ESA_CCI_SM_combined': r'm^3 m^{-3}',
    'SMOS': r'm^3 m^{-3}'
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

    values = values[~np.isnan(values)]

    # use seaborn library for boxplot
    sns.set_palette('RdYlBu_r')
    sns.set_style("whitegrid")
    sns.boxplot(y=values, width=0.15, showfliers=False)
    sns.despine()

    plt.title('Validation {} ({}) vs {} ({})'.format(
        validation_run.data_dataset.pretty_name,
        validation_run.data_version.pretty_name,
        validation_run.ref_dataset.pretty_name,
        validation_run.ref_version.pretty_name))
    plt.ylabel(label + _metric_description[variable].format(_metric_units[unit_ref]))
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

    ax = plt.axes(projection=ccrs.PlateCarree())
    cm = plt.cm.get_cmap(_colormaps[variable])
    ax.outline_patch.set_linewidth(0.2)

    v_min = _metric_value_ranges[variable][0]
    v_max = _metric_value_ranges[variable][1]

    # do scatter plot for ISMN and heatmap for everything else
    if validation_run.ref_dataset.short_name == globals.ISMN:
        # change size of markers dependent on zoom level
        lon_interval = max(lons) - min(lons)
        markersize = 1.5 * (360 / lon_interval)
        the_plot = plt.scatter(lons, lats, c=values, cmap=cm, s=markersize, vmin=v_min, vmax=v_max,
                               edgecolors='black', linewidths=0.05, zorder=3)
    else:
        lats_map = np.arange(89.875, -60, -0.25)
        lons_map = np.arange(-179.875, 180, 0.25)
        values_map = np.empty((len(lats_map), len(lons_map)))
        values_map[:] = np.nan

        for i in range(0, len(values)):
            values_map[np.where(lats_map == lats[i])[0][0]][np.where(lons_map == lons[i])[0][0]] = values[i]

        extent = [-179.875, 179.875, -59.875, 89.875]
        the_plot = plt.imshow(values_map, cmap=cm, interpolation='none', extent=extent,
                              vmin=v_min, vmax=v_max, zorder=1)

    plt.title('Validation {} ({}) vs {} ({})'.format(
        validation_run.data_dataset.pretty_name,
        validation_run.data_version.pretty_name,
        validation_run.ref_dataset.pretty_name,
        validation_run.ref_version.pretty_name), fontsize=8)
    ax.coastlines(linewidth=0.2, zorder=2)
    ax.add_feature(cfeature.STATES, linewidth=0.05, zorder=2)
    ax.add_feature(cfeature.BORDERS, linewidth=0.1, zorder=2)
    ax.add_feature(cfeature.LAND, color='white', zorder=0)

    # add gridlines
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.2, color='gray', alpha=0.5, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_left = False
    gl.xlocator = mticker.FixedLocator(np.arange(-180, 181, 45))
    gl.ylocator = mticker.FixedLocator(np.arange(-90, 91, 30))
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 4, 'color': 'black'}
    gl.ylabel_style = {'size': 4, 'color': 'black'}

    # add colorbar
    cbar = plt.colorbar(the_plot, orientation='horizontal', pad=0.05, aspect=40)
    cbar.set_label(label + _metric_description[variable].format(_metric_units[unit_ref]), size=5)
    cbar.outline.set_linewidth(0.2)
    cbar.outline.set_edgecolor('black')
    cbar.ax.tick_params(width=0.2, labelsize=4)

    plt.savefig(png_filename, bbox_inches='tight', pad_inches=0.1, dpi=200)
    plt.savefig(svg_filename, bbox_inches='tight', pad_inches=0.1, dpi=200)
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
            with netCDF4.Dataset(validation_run.output_file.path) as ds:
                values = ds.variables[metric][:]

            file1, file2 = generate_boxplot(validation_run, outfolder, metric, METRICS[metric], values, unit_ref)
            arcname = path.basename(file1)
            myzip.write(file1, arcname=arcname)
            arcname = path.basename(file2)
            myzip.write(file2, arcname=arcname)
            remove(file2) # we don't need the vector image anywhere but in the zip

            file1, file2 = generate_overview_map(validation_run, outfolder, metric, METRICS[metric], values, unit_ref)
            arcname = path.basename(file1)
            myzip.write(file1, arcname=arcname)
            arcname = path.basename(file2)
            myzip.write(file2, arcname=arcname)
            remove(file2) # we don't need the vector image anywhere but in the zip
