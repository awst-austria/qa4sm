import logging
from os import path

from ascat.read_native.cdr import AscatGriddedNcTs
from c3s_sm.interface import C3STs as c3s_read
from ecmwf_models.interface import ERATs
from esa_cci_sm.interface import CCITs
from gldas.interface import GLDASTs
from ismn.interface import ISMN_Interface
from smap_io.interface import SMAPTs
from smos.smos_ic.interface import SMOSTs
from pynetcf.time_series import GriddedNcTs

from qa4sm_preprocessing.cgls_hr_ssm_swi.reader import S1CglsTs
from qa4sm_preprocessing.reading import StackImageReader
from qa4sm_preprocessing.reading import GriddedNcOrthoMultiTs

from validator.validation import globals
from validator.validation.util import first_file_in

from pytesmo.validation_framework.adapters import TimestampAdapter
from validator.models import UserDatasetFile

__logger = logging.getLogger(__name__)


def create_reader(dataset, version) -> GriddedNcTs:
    """
    Create basic readers (without any adapters / filters) for a dataset version
    """

    reader = None  # reader class, inherits pynetcf time series module

    folder_name = path.join(dataset.storage_path, version.short_name)

    if dataset.short_name == globals.ISMN:
        reader = ISMN_Interface(folder_name)

    if dataset.short_name == globals.C3SC:
        c3s_data_folder = path.join(folder_name, 'TCDR/063_images_to_ts/combined-daily')
        reader = c3s_read(c3s_data_folder, ioclass_kws={'read_bulk': True})

    if (dataset.short_name == globals.CCIC or
        dataset.short_name == globals.CCIA or
        dataset.short_name == globals.CCIP):
        reader = CCITs(folder_name, ioclass_kws={'read_bulk':True})

    if dataset.short_name == globals.GLDAS:
        reader = GLDASTs(folder_name, ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.SMAP_L3:
        smap_data_folder = path.join(folder_name, 'netcdf')
        reader = SMAPTs(smap_data_folder, ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.ASCAT:
        ascat_data_folder = path.join(folder_name, 'data')
        ascat_grid_path = first_file_in(path.join(folder_name, 'grid'), '.nc')
        fn_format = "{:04d}"
        reader = AscatGriddedNcTs(path=ascat_data_folder, fn_format=fn_format,
                                  grid_filename=ascat_grid_path, static_layer_path=None,
                                  ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.SMOS_IC:
        reader = SMOSTs(folder_name, ioclass_kws={'read_bulk':True})

    if dataset.short_name == globals.ERA5:
        reader = ERATs(folder_name, ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.ERA5_LAND:
        reader = ERATs(folder_name, ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.CGLS_SCATSAR_SWI1km:
        reader = S1CglsTs(folder_name)

    if dataset.short_name == globals.CGLS_CSAR_SSM1km:
        reader = S1CglsTs(folder_name)

    if dataset.short_name == globals.SMOS_L3:
        reader = SMOSTs(folder_name, ioclass_kws={'read_bulk': True})

    if dataset.user:
        file = UserDatasetFile.objects.get(dataset=dataset)
        stackreader = StackImageReader(
            dataset.storage_path,  # path to the netCDF file
            file.variable.short_name,  # name of the soil moisture variable
            latname=file.latname,  # e.g. "lat"
            lonname=file.lonname,  # e.g. "lon"
            timename=file.timename  # e.g. "time"
        )
        # reader = stackreader
        tsreader = stackreader.repurpose(
            file.get_raw_file_path + "timeseries",  # path to the timeseries directory
            # if overwrite=False, it checks if the timeseries directory
            # already exists, and if it does, it just returns the reader
            # without repeating the preprocessing
            overwrite=False,
        )

        reader = tsreader

    if not reader:
        raise ValueError("Reader for dataset '{}' not available".format(dataset))

    return reader


def adapt_timestamp(reader, dataset):
    """Adapt the reader to include the specified time offset"""
    if dataset.short_name == globals.SMOS_L3:
        tadapt_kwargs = {
            'time_offset_fields': 'Mean_Acq_Time_Seconds',
            'time_units': 's',
            'base_time_field': 'Mean_Acq_Time_Days',
            'base_time_reference': '2000-01-01',
        }

    elif dataset.short_name == globals.SMOS_IC:
        tadapt_kwargs = {
            'time_offset_fields': ['UTC_Seconds', 'UTC_Microseconds'],
            'time_units': ['s', 'us'],
            'base_time_field': 'Days',
            'base_time_reference': '2000-01-01',
        }

    # No adaptation needed
    else:
        return reader

    __logger.debug(
        f"{dataset.short_name} adapted to account for the time offset"
    )

    # Adapt the reader with the exact timestamps
    return TimestampAdapter(reader, **tadapt_kwargs)
