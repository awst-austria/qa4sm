import numpy as np

import pygeogrids.netcdf  # bugfix
from ismn.interface import ISMN_Interface
from pygeobase.io_base import GriddedBase

from validator.validation.readers import create_reader


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

            if isinstance(gpis, np.ma.MaskedArray):
                gpis = gpis.compressed()
                lons = lons.compressed()
                lats = lats.compressed()

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
            jobs.append((gpis, lons, lats))
            total_points += len(gpis)

    else:
        raise ValueError("Don't know how to get gridpoints and generate jobs for reader {}".format(ref_reader))

    return total_points, jobs
