# -*- coding: utf-8 -*-

"""
Module description
"""
# TODO:
#   (+)
# ---------
# NOTES:
#   -

from ismn.interface import ISMN_Interface
import sys
import matplotlib.pyplot as plt
import numpy as np
import cartopy
import json
import cartopy.crs as ccrs
from matplotlib.patches import Rectangle


class ISMN_Plotter(ISMN_Interface):
    def __init__(self, path_to_data, networks_to_use=None):
        super(ISMN_Plotter, self).__init__(path_to_data, network=networks_to_use)

    def plot_station_locations(self, variable='soil moisture',
                               min_depth=0, max_depth=999., filename=None,
                               check_only_depth_from=False):
        """
        plots available stations on a world map in robinson projection

        Parameters
        ----------
        variable : str, optional (default: 'soil moisture')
            Variable that is use to find stations that measure it
        min_depth : float, optional (default: 0.)
            Only stations that measure variable below this depth are considered.
        max_depth : float or None, optional (default: None.)
            Only stations that measure variable above this depth are considered.
            If None is passed, only the min_depth is considered.

        Returns
        -------
        fig: matplotlib.Figure
            created figure instance. If axes was given this will be None.
        ax: matplitlib.Axes
            used axes instance.
        """
        if not (sys.version_info[0] == 3 and sys.version_info[1] == 4):
            colormap = plt.get_cmap('tab20')
        else:
            colormap = plt.get_cmap('Set1')

        uniq_networks = self.list_networks()
        colorsteps = np.arange(0, 1, 1 / float(uniq_networks.size))
        rect = []

        lons, lats, values = [], [], []

        network_count = 0
        station_count = 0
        sensors_count = 0

        for j, network in enumerate(uniq_networks):
            network_counted = False
            netcolor = colormap(colorsteps[j])
            rect.append(Rectangle((0, 0), 1, 1, fc=netcolor))

            stationnames = self.list_stations(network)
            geo_json_features = []
            for stationname in stationnames:
                station_counted = False
                station = self.get_station(stationname, network)
                station_vars = station.get_variables()
                geo_json_feature = {}
                geo_json_feature['type'] = 'Feature'
                feature_properties = {}
                feature_properties['station_name'] = station.station
                feature_properties['depth_from'] = '{}'.format(station.depth_from)
                feature_properties['depth_to'] = '{}'.format(station.depth_to)
                feature_properties['network'] = station.network

                geo_json_feature['properties'] = feature_properties

                geo_json_geometry = {'type': 'Point', 'coordinates': [station.longitude, station.latitude]}
                geo_json_feature['geometry'] = geo_json_geometry
                geo_json_features.append(geo_json_feature)
                if variable not in station_vars:
                    continue

                station_depths_from, station_depths_to = station.get_depths(variable)

                for depth_from, depth_to in zip(station_depths_from, station_depths_to):
                    if check_only_depth_from:
                        if (depth_from < min_depth) or (depth_from > max_depth):
                            # skip depths outside of the passed range
                            continue
                    else:
                        if (depth_from < min_depth) or (depth_to > max_depth):
                            continue

                    # from here we actually have valid data
                    if not station_counted:
                        station_count += 1
                        station_counted = True

                    if not network_counted:
                        network_count += 1
                        network_counted = True

                    # we check only depth_from here
                    if check_only_depth_from:
                        ind_sensors = np.where((variable == station.variables) &
                                               (depth_from == station.depth_from))[0]
                    else:
                        ind_sensors = np.where((variable == station.variables) &
                                               (depth_to == station.depth_to) &
                                               (depth_from == station.depth_from))[0]

                    sensors = station.sensors[ind_sensors]

                    for sensor in sensors:
                        lons.append(station.longitude)
                        lats.append(station.latitude)
                        values.append(colorsteps[j])
                        sensors_count += 1

            geo_json_feature_collection = {}
            geo_json_feature_collection['type'] = 'FeatureCollection'
            geo_json_feature_collection['features'] = geo_json_features
            print(geo_json_feature_collection)
            text_file = open('networks/' + station.network + ".json", "w")
            n = text_file.write(json.dumps(geo_json_feature_collection))
            text_file.close()

        postfix_depth = "when only considering depth_from of the sensor" if check_only_depth_from else ''

        feedback = "{} valid sensors in {} stations in {} networks (of {} potential networks) \n" \
                   "for variable '{}' between {} and {} m depth \n {}".format(
            sensors_count, station_count, network_count, len(uniq_networks), variable, min_depth, max_depth,
            postfix_depth)

        print(feedback)

        # plotting --->
        fig = plt.figure(num=None, figsize=(8, 4), facecolor='w', edgecolor='k')

        data_crs = ccrs.PlateCarree()

        imax = plt.axes(projection=ccrs.Robinson())
        imax.coastlines(resolution='110m', color='black', linewidth=0.25)

        imax.add_feature(cartopy.feature.OCEAN, zorder=0)
        imax.add_feature(cartopy.feature.LAND, zorder=0, facecolor='white')
        imax.add_feature(cartopy.feature.STATES, linewidth=0.05, zorder=2)
        imax.add_feature(cartopy.feature.BORDERS, linewidth=0.1, zorder=2)

        ax = plt.scatter(lons, lats, s=10,
                         zorder=3, transform=data_crs)

        nrows = 8. if len(uniq_networks) > 8 else len(uniq_networks)
        ncols = int(uniq_networks.size / nrows)
        if ncols == 0:
            ncols = 1

        handles, labels = imax.get_legend_handles_labels()
        lgd = imax.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.1))

        plt.legend(rect, uniq_networks.tolist(), loc='upper center', ncol=ncols,
                   bbox_to_anchor=(0.5, -0.05), fontsize=4)
        text = imax.text(0.5, 1.2, feedback, transform=imax.transAxes, fontsize='xx-small',
                         horizontalalignment='center')

        fig.set_size_inches([6, 3.5 + 0.25 * nrows])
        if filename is not None:
            fig.savefig(filename, bbox_extra_artists=(lgd, text), dpi=300)
            plt.close(fig)
        else:
            return fig, imax


if __name__ == '__main__':
    ds = ISMN_Plotter(r"/mnt/qa4sm/qa4sm_sat_data/ISMN/ISMN_V20191211", networks_to_use=None)
    ds.plot_station_locations('soil moisture', 0, 0.1, 'asd.jpg', check_only_depth_from=True)
