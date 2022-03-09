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

from validator.validation import globals
from validator.validation.util import first_file_in

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
        reader = c3s_read(c3s_data_folder, ioclass_kws={'read_bulk':True})

    if (dataset.short_name == globals.CCIC or
        dataset.short_name == globals.CCIA or
        dataset.short_name == globals.CCIP):
        reader = CCITs(folder_name, ioclass_kws={'read_bulk':True})

    if dataset.short_name == globals.GLDAS:
        reader = GLDASTs(folder_name, ioclass_kws={'read_bulk':True})

    if dataset.short_name == globals.SMAP:
        smap_data_folder = path.join(folder_name, 'netcdf')
        reader = SMAPTs(smap_data_folder, ioclass_kws={'read_bulk':True})

    if dataset.short_name == globals.ASCAT:
        ascat_data_folder = path.join(folder_name, 'data')
        ascat_grid_path = first_file_in(path.join(folder_name, 'grid'), '.nc')
        fn_format = "{:04d}"
        reader = AscatGriddedNcTs(path=ascat_data_folder, fn_format=fn_format, grid_filename=ascat_grid_path,
                         static_layer_path=None, ioclass_kws={'read_bulk':True})
        reader = AscatGriddedNcTs(path=ascat_data_folder, fn_format=fn_format,
                         grid_filename=ascat_grid_path, static_layer_path=None,
                         ioclass_kws={'read_bulk':True})

    if dataset.short_name == globals.SMOS_IC:
        reader = SMOSTs(folder_name, ioclass_kws={'read_bulk':True})

    if dataset.short_name == globals.ERA5:
        reader = ERATs(folder_name, ioclass_kws={'read_bulk':True})

    if dataset.short_name == globals.ERA5_LAND:
        reader = ERATs(folder_name, ioclass_kws={'read_bulk':True})

    if dataset.short_name == globals.CGLS_SCATSAR_SWI1km:
        reader = S1CglsTs(folder_name)

    if dataset.short_name == globals.CGLS_CSAR_SSM1km:
        reader = S1CglsTs(folder_name)

    if not reader:
        raise ValueError("Reader for dataset '{}' not available".format(dataset))


    return reader
