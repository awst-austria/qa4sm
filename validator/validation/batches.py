import numpy as  np
import pandas as pd

from ismn.interface import ISMN_Interface
from pygeobase.io_base import GriddedBase

from validator.models import DataFilter
from validator.validation.readers import create_reader
from validator.validation.filters import setup_filtering

# function to retrieve depth_from and depth_to from the database
def get_depths_params(param_filters):
    default_depth = DataFilter.objects.get(name='FIL_ISMN_DEPTH').default_parameter
    default_depth = [float(depth) for depth in default_depth.split(',')]
    depth_from = default_depth[0]
    depth_to = default_depth[1]

    param_name_list = [pfil.filter.name for pfil in list(param_filters)]
    if "FIL_ISMN_DEPTH" in param_name_list:
        ind = param_name_list.index('FIL_ISMN_DEPTH')
        depth_from = float(param_filters[ind].parameters.split(',')[0])
        depth_to = float(param_filters[ind].parameters.split(',')[1])

    if depth_to < 0 or depth_from <0:
        raise ValueError("the depth range can not be negative")
    if depth_to < depth_from:
        raise ValueError("depth_to can not be less than depth_from")

    return [depth_from, depth_to]


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

    # we do the dance with the filtering below because filter may actually change the original reader, see ismn network selection
    ref_reader = setup_filtering(ref_reader, list(validation_run.reference_configuration.filters.all()),\
                                 list(validation_run.reference_configuration.parametrisedfilter_set.all()),\
                                 validation_run.reference_configuration.dataset, validation_run.reference_configuration.variable)
    while(hasattr(ref_reader, 'cls')):
        ref_reader = ref_reader.cls

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

        depth_from, depth_to = get_depths_params(validation_run.reference_configuration.parametrisedfilter_set.all())

        ids = ref_reader.get_dataset_ids(variable=validation_run.reference_configuration.variable.pretty_name, min_depth=depth_from, max_depth=depth_to, groupby='network')

        def reshape_meta(meta):
            reshaped = {}
            for key, value in meta.items():
                meta_value = value[0][0]
                if isinstance(meta_value, pd.Timestamp):
                    meta_value = meta_value.to_numpy()
                reshaped[key] = meta_value

            return reshaped

        jobs = []
        for network, net_ids in ids.items():
            lons, lats, meta_list = [], [], []
            for idx in net_ids:
                meta = ref_reader.read_ts(idx, return_meta=True)[1]
                meta = reshape_meta(meta)
                lons.append(meta['longitude'])
                lats.append(meta['latitude'])
                meta_list.append(meta)
            gpis = net_ids
            gpis, lons, lats = np.array(gpis), np.array(lons), np.array(lats)

            gpis, lons, lats, index = _geographic_subsetting(gpis, lons, lats, validation_run.min_lat, validation_run.min_lon, validation_run.max_lat, validation_run.max_lon)

            if len(gpis) > 0:
                jobs.append((gpis, lons, lats, meta_list))
                total_points += len(gpis)

    else:
        raise ValueError("Don't know how to get gridpoints and generate jobs for reader {}".format(ref_reader))

    return total_points, jobs
