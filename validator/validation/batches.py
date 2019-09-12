import numpy as np

import pygeogrids.netcdf  # bugfix
from ismn.interface import ISMN_Interface
from pygeobase.io_base import GriddedBase

from validator.validation.readers import create_reader

# very basic geographic subsetting with only a bounding box. simple should also be quick :-)
def _geographic_subsetting(gpis, lons, lats, min_lat, min_lon, max_lat, max_lon):
    if (min_lat is not None and min_lon is not None and max_lat is not None and max_lon is not None) :

        # shift back to "normal" coordinates if shifted to the right
        if (min_lon > 180.0):
            shift = round(min_lon / 360.0) * 360.0
            min_lon -= shift
            max_lon -= shift

        # shift back to "normal" coordinates if shifted to the left
        if (max_lon < -180.0):
            shift = round(max_lon / -360.0) * 360.0
            min_lon += shift
            max_lon += shift

        ## handle special case of bounding box across antimeridian
        if((max_lon > 180.0) or (min_lon < -180.0) ):
            if(max_lon > 180.0):
                new_min_lon = min_lon
                new_max_lon = max_lon - 360.0
            if(min_lon < -180.0):
                new_min_lon = min_lon + 360.0
                new_max_lon = max_lon

            index = np.where(((lats <= max_lat) & (lats >= min_lat) & (lons <= 180.0) & (lons >= new_min_lon)) |
                             ((lats <= max_lat) & (lats >= min_lat) & (lons <= new_max_lon) & (lons >= -180.0)))
        ## handle "normal" case of bounding box not across antimeridian
        else:
            index = np.where((lats <= max_lat) & (lats >= min_lat) & (lons <= max_lon) & (lons >= min_lon))

        gpis = gpis[index]
        lats = lats[index]
        lons = lons[index]

    # if no geographic subsetting, make an index that covers all gpis
    else:
        index = np.arange(len(gpis))

    return gpis, lons, lats, index

def create_jobs(validation_run):
    jobs = []
    total_points = 0

    ref_reader = create_reader(validation_run.reference_configuration.dataset, validation_run.reference_configuration.version)
    ref_reader = ref_reader.reader

    # if we've got data on a grid, process one cell at a time
    if isinstance(ref_reader, GriddedBase):
        cells = ref_reader.grid.get_cells()

        jobs = []
        for cell in cells:
            gpis, lons, lats = ref_reader.grid.grid_points_for_cell(cell)

            gpis, lons, lats, index = _geographic_subsetting(gpis, lons, lats, validation_run.min_lat, validation_run.min_lon, validation_run.max_lat, validation_run.max_lon)

            if isinstance(gpis, np.ma.MaskedArray):
                gpis = gpis.compressed()
                lons = lons.compressed()
                lats = lats.compressed()

            if len(gpis) > 0:
                jobs.append((gpis, lons, lats))
                total_points += len(gpis)

    # if we've got ISMN data, process one network at a time
    elif isinstance(ref_reader, ISMN_Interface):
        ids = ref_reader.get_dataset_ids(variable=validation_run.reference_configuration.variable.pretty_name, min_depth=0, max_depth=0.1)
        mdata = ref_reader.metadata[ids]
        networks = np.unique(mdata['network'])

        jobs = []
        for network in networks:
            net_ids = mdata['network'] == network
            net_data = mdata[net_ids]
            lons = net_data['longitude']
            lats = net_data['latitude']
            gpis = ids[net_ids]

            gpis, lons, lats, index = _geographic_subsetting(gpis, lons, lats, validation_run.min_lat, validation_run.min_lon, validation_run.max_lat, validation_run.max_lon)

            if len(gpis) > 0:
                jobs.append((gpis, lons, lats))
                total_points += len(gpis)

    else:
        raise ValueError("Don't know how to get gridpoints and generate jobs for reader {}".format(ref_reader))

    return total_points, jobs
