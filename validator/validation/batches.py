import numpy as np
import pandas as pd
from typing import Union
import logging

from ismn.interface import ISMN_Interface
from pygeobase.io_base import GriddedBase

from validator.models import DataFilter
from validator.validation import globals
from validator.validation.readers import ReaderWithTsExtension

__logger = logging.getLogger(__name__)


# function to retrieve depth_from and depth_to from the database
def get_depths_params(param_filters):
    default_depth = DataFilter.objects.get(
        name='FIL_ISMN_DEPTH').default_parameter
    default_depth = [float(depth) for depth in default_depth.split(',')]
    depth_from = default_depth[0]
    depth_to = default_depth[1]

    param_name_list = [pfil.filter.name for pfil in list(param_filters)]
    if "FIL_ISMN_DEPTH" in param_name_list:
        ind = param_name_list.index('FIL_ISMN_DEPTH')
        depth_from = float(param_filters[ind].parameters.split(',')[0])
        depth_to = float(param_filters[ind].parameters.split(',')[1])

    if depth_to < 0 or depth_from < 0:
        raise ValueError("the depth range can not be negative")
    if depth_to < depth_from:
        raise ValueError("depth_to can not be less than depth_from")

    return [depth_from, depth_to]


def get_meta_filter_dict(filters) -> Union[dict, None]:
    """
    Convert sensor / station metadata based filters to dict used by the ISMN
    Interface if any of the relevant filters are activated.

    Parameters:
    ----------
    filters: list[DataFilter]
        Filters (not parametised) to check.
    """
    names = [filter.name for filter in list(filters)]
    filter_meta_dict = {}
    if "FIL_ISMN_FRM_representative" in names:
        filter_meta_dict['frm_class'] = ['very representative',
                                         'representative']

    return filter_meta_dict if len(filter_meta_dict) != 0 else None


# very basic geographic subsetting with only a bounding box. simple should
# also be quick :-)
def _geographic_subsetting(gpis, lons, lats, min_lat, min_lon, max_lat,
                           max_lon):
    if (min_lat is not None and min_lon is not None and max_lat is not None
            and max_lon is not None):

        # shift back to "normal" coordinates if shifted to the right
        if min_lon > 180.0:
            shift = round(min_lon / 360.0) * 360.0
            min_lon -= shift
            max_lon -= shift

        # shift back to "normal" coordinates if shifted to the left
        if max_lon < -180.0:
            shift = round(max_lon / -360.0) * 360.0
            min_lon += shift
            max_lon += shift

        # handle special case of bounding box across antimeridian
        if (max_lon > 180.0) or (min_lon < -180.0):
            if max_lon > 180.0:
                new_min_lon = min_lon
                new_max_lon = max_lon - 360.0
            if min_lon < -180.0:
                new_min_lon = min_lon + 360.0
                new_max_lon = max_lon

            index = np.where(((lats <= max_lat) & (lats >= min_lat) & (
                        lons <= 180.0) & (lons >= new_min_lon)) |
                             ((lats <= max_lat) & (lats >= min_lat) & (
                                         lons <= new_max_lon) & (
                                          lons >= -180.0)))
        # handle "normal" case of bounding box not across antimeridian
        else:
            index = np.where(
                (lats <= max_lat) & (lats >= min_lat) & (lons <= max_lon) & (
                            lons >= min_lon))

        gpis = gpis[index]
        lats = lats[index]
        lons = lons[index]

    # if no geographic subsetting, make an index that covers all gpis
    else:
        index = np.arange(len(gpis))

    return gpis, lons, lats, index


def create_jobs(
        validation_run,
        reader,
        dataset_config,
        return_points=True,
) -> Union[tuple, list]:
    """
    Create jobs for validation run. The reference reader is passed here.

    Parameters
    ----------
    validation_run: models.validation_run.ValidationRun object
        Configuration of the run
    reader: object
        reader of the reference
    dataset_config: models.dataset_configuration.DatasetConfiguration object
        configuration of the dataset that the reader belongs to
    return_points: bool, default is True
        If True, return total_points

    Returns
    -------
    jobs: list of tuples
        each tuple has the shape (gpis, lons, lats). Optionally a list of
        metadata is included
    total_points: int
        n of validation points
    """
    if dataset_config is None:
        raise ValueError(
            "A dataset configuration has not been provided for the jobs "
            "generation"
        )

    total_points = 0

    # if we've got data on a grid, process one cell at a time
    if isinstance(reader, GriddedBase) or isinstance(reader,
                                                     ReaderWithTsExtension):
        cells = reader.grid.get_cells()

        jobs = []
        for cell in cells:
            gpis, lons, lats = reader.grid.grid_points_for_cell(cell)

            gpis, lons, lats, index = _geographic_subsetting(
                gpis, lons, lats, validation_run.min_lat,
                validation_run.min_lon, validation_run.max_lat,
                validation_run.max_lon
            )

            if isinstance(gpis, np.ma.MaskedArray):
                gpis = gpis.compressed()
                lons = lons.compressed()
                lats = lats.compressed()

            if len(gpis) > 0:
                jobs.append((gpis, lons, lats))
                total_points += len(gpis)

    # if we've got ISMN data, process one network at a time
    elif isinstance(reader, ISMN_Interface):
        depth_from, depth_to = get_depths_params(
            dataset_config.parametrisedfilter_set.all()
        )
        filter_meta_dict = get_meta_filter_dict(
            list(dataset_config.filters.all()))

        ids = reader.get_dataset_ids(
            variable=dataset_config.variable.short_name,
            min_depth=depth_from,
            max_depth=depth_to,
            filter_meta_dict=filter_meta_dict,
            groupby='network',
        )

        def reshape_meta(metadata):
            # reshape metadata dictionary to facilitate use
            reshaped = {}
            for key, value in metadata.items():
                meta_value = value[0][0]
                if isinstance(meta_value, pd.Timestamp):
                    meta_value = meta_value.to_numpy()
                reshaped[key] = meta_value
            # parse information on the measuring depth from the instument
            # metadata
            reshaped[globals.MEASURE_DEPTH_FROM] = \
            metadata[globals.INSTRUMENT_META][0][1]
            reshaped[globals.MEASURE_DEPTH_TO] = \
            metadata[globals.INSTRUMENT_META][0][2]

            return reshaped

        jobs = []
        for network, net_ids in ids.items():
            lons, lats, meta_list = [], [], []
            for idx in net_ids:
                meta = reader.read_metadata(idx, format="dict")
                meta = reshape_meta(meta)
                lons.append(meta['longitude'])
                lats.append(meta['latitude'])
                meta_list.append(meta)
            gpis = net_ids
            gpis, lons, lats = np.array(gpis), np.array(lons), np.array(lats)

            gpis, lons, lats, index = _geographic_subsetting(
                gpis, lons, lats, validation_run.min_lat,
                validation_run.min_lon, validation_run.max_lat,
                validation_run.max_lon
            )

            meta_list = np.array(meta_list)[index]

            if len(gpis) > 0:
                jobs.append((gpis, lons, lats, meta_list))
                total_points += len(gpis)

    else:
        raise ValueError(
            "Don't know how to get gridpoints and generate jobs for reader {"
            "}".format(
                reader))

    if not return_points:
        return jobs

    return total_points, jobs


def create_upscaling_lut(
        validation_run,
        datasets,
        spatial_ref_name
) -> dict:
    """
    Create a lookup table that aggregates the non-reference measurement
    points falling under the same reference
    pixel

    Parameters
    ----------
    validation_run: models.validation_run.ValidationRun object
        Configuration of the run
    datasets : dict of dicts
        :Keys: string, datasets names
        :Values: dict, containing the following fields (see pytesmo
        DataManager for details):
            *'class'
            *'columns'
            *'args': list, optional
            *'kwargs': dict, optional
            *'grids_compatible': boolean, optional
            *'use_lut': boolean, optional
            *'lut_max_dist': float, optional
    ref_name: str
        Name of the reference dataset

    Returns
    -------
    lut: dict
        lookup table with shape {'other_dataset':{ref gpi: [other gpis]}}
    """
    ref_reader = datasets[spatial_ref_name]["class"]
    ref_grid = ref_reader.grid

    lut = {}
    # a bit of a kack to match dataset name and configuation
    for other_name, other_config in zip(
            datasets.keys(),
            validation_run.dataset_configurations.all(),
    ):
        if other_name == spatial_ref_name:
            continue
        else:
            other_reader = datasets[other_name]["class"]
            while hasattr(other_reader, 'cls'):
                other_reader = other_reader.cls
            # get all 'other' points, divided in 'jobs'
            other_points_jobs = create_jobs(
                validation_run=validation_run,
                reader=other_reader,
                dataset_config=other_config,
                return_points=False
            )
            if not other_points_jobs:
                __logger.debug(
                    "There are no points to average in the selected dataset "
                    "of {}. Check the filtering configuration".format(
                        other_config.dataset)
                )
                # make sure there is always a key, even when no points are
                # found
                lut[other_name] = []
            else:
                # iterate from the side of the non-reference
                other_lut = {}
                for other_points in other_points_jobs:
                    gpis, lons, lats = other_points[0], other_points[1], \
                    other_points[2]
                    for gpi, lon, lat in zip(gpis, lons, lats):
                        # list all non-ref points under the same ref gpi
                        ref_gpi = ref_grid.find_nearest_gpi(lon, lat)[0]
                        # todo: implement methods here to combine irregular
                        #  grids
                        if ref_gpi in other_lut.keys():
                            other_lut[ref_gpi].append((gpi, lon, lat))
                        else:
                            other_lut[ref_gpi] = [(gpi, lon, lat)]

                lut[other_name] = other_lut

    return lut
