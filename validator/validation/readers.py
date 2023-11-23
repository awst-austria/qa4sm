import logging
from os import path
import numpy as np

from ascat.read_native.cdr import AscatGriddedNcTs
from c3s_sm.interface import C3STs as c3s_read
from ecmwf_models.interface import ERATs
from esa_cci_sm.interface import CCITs
from gldas.interface import GLDASTs
from ismn.interface import ISMN_Interface
from ismn.custom import CustomSensorMetadataCsv
from smap_io.interface import SMAPTs
from smos.smos_ic.interface import SMOSTs
from pynetcf.time_series import GriddedNcTs

from qa4sm_preprocessing.cgls_hr_ssm_swi.reader import S1CglsTs
from qa4sm_preprocessing.reading import GriddedNcOrthoMultiTs, GriddedNcContiguousRaggedTs

from validator.validation import globals
from validator.validation.util import first_file_in

from pytesmo.validation_framework.adapters import TimestampAdapter, BasicAdapter
from validator.models import UserDatasetFile
import pandas as pd

__logger = logging.getLogger(__name__)

class SBPCAReader(GriddedNcOrthoMultiTs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self, *args, **kwargs) -> pd.DataFrame:
        ts = super(SBPCAReader, self).read(*args, **kwargs)
        if (ts is not None) and not ts.empty:
            ts = ts[ts.index.notnull()]
            for col in ['Chi_2_P', 'M_AVA0', 'N_RFI_X', 'N_RFI_Y', 'RFI_Prob',
                        'Science_Flags']:
                if col in ts.columns:
                    ts[col] = ts[col].fillna(0)
            ts = ts.dropna(subset='Soil_Moisture')
            ts = ts.dropna(subset='acquisition_time')
        return ts

def create_reader(dataset, version) -> GriddedNcTs:
    """
    Create basic readers (without any adapters / filters) for a dataset version
    """

    reader = None  # reader class, inherits pynetcf time series module

    folder_name = path.join(dataset.storage_path, version.short_name)

    if dataset.short_name == globals.ISMN:
        if path.isfile(path.join(folder_name, 'frm_classification.csv')):
            custom_meta_readers = [
                CustomSensorMetadataCsv(
                    path.join(folder_name, 'frm_classification.csv'),
                    fill_values={'frm_class': 'undeducible'},
                ),
            ]
        else:
            custom_meta_readers = None
        reader = ISMN_Interface(folder_name,
                                custom_meta_reader=custom_meta_readers)

    if dataset.short_name == globals.C3SC:
        c3s_data_folder = path.join(folder_name, 'TCDR/063_images_to_ts/combined-daily')
        reader = c3s_read(c3s_data_folder, ioclass_kws={'read_bulk': True})

    if (dataset.short_name == globals.CCIC or
            dataset.short_name == globals.CCIA or
            dataset.short_name == globals.CCIP):
        reader = CCITs(folder_name, ioclass_kws={'read_bulk': True})

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
                                  grid_filename=ascat_grid_path,
                                  static_layer_path=None,
                                  ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.SMOS_IC:
        reader = SMOSTs(folder_name, ioclass_kws={'read_bulk': True})

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

    if dataset.short_name == globals.SMOS_L2:
        reader = GriddedNcOrthoMultiTs(folder_name, ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.SMAP_L2:
        reader = GriddedNcOrthoMultiTs(folder_name, ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.SMOS_SBPCA:
        reader = SBPCAReader(folder_name, ioclass_kws={'read_bulk': True})

    if dataset.user and len(dataset.user_dataset.all()):
        file = UserDatasetFile.objects.get(dataset=dataset)
        if file.file_name.endswith('nc') or file.file_name.endswith('nc4'):
            reader = GriddedNcOrthoMultiTs(file.get_raw_file_path + "/timeseries", ioclass_kws={'read_bulk': True})
        elif file.file_name.endswith('zip'):
            reader = GriddedNcContiguousRaggedTs(file.get_raw_file_path + "/timeseries",
                                                 ioclass_kws={'read_bulk': True})

    if not reader:
        raise ValueError("Reader for dataset '{}' not available".format(dataset))

    return reader


def adapt_timestamp(reader, dataset, version):
    """Adapt the reader to include the specified time offset"""
    if dataset.short_name == globals.SMOS_L3:
        tadapt_kwargs = {
            'time_offset_fields': 'Mean_Acq_Time_Seconds',
            'time_units': 's',
            'base_time_field': 'Mean_Acq_Time_Days',
            'base_time_reference': '2000-01-01',
        }

    elif dataset.short_name == globals.SMOS_L2:
        tadapt_kwargs = {
            'time_offset_fields': 'Seconds',
            'time_units': 's',
            'base_time_field': 'Days',
            'base_time_units': 'ns',
            'base_time_reference': '2000-01-01',
        }

    elif dataset.short_name == globals.SMOS_SBPCA:
        tadapt_kwargs = {
            'base_time_field': 'acquisition_time',
            'base_time_reference': '2000-01-01T00:00:00',
            'base_time_units': 's',
            'time_offset_fields': None,
            'time_units': None,
        }

    elif dataset.short_name == globals.SMOS_IC:
        tadapt_kwargs = {
            'time_offset_fields': ['UTC_Seconds', 'UTC_Microseconds'],
            'time_units': ['s', 'us'],
            'base_time_field': 'Days',
            'base_time_reference': '2000-01-01',
        }

    elif dataset.short_name == globals.SMAP_L2:
        tadapt_kwargs = {
            'base_time_field': 'acquisition_time',
            'base_time_reference': '2000-01-01T12:00:00',
            'base_time_units': 's',
            'time_offset_fields': None,
            'time_units': None,
        }

    elif dataset.short_name == globals.SMAP_L3 and version.short_name == globals.SMAP_V6_PM:
        tadapt_kwargs = {
            'base_time_field': 'tb_time_seconds',
            'base_time_reference': '2000-01-01T12:00:00',
            'base_time_units': 's',
            'time_offset_fields': None,
            'time_units': None,
        }

    # No adaptation needed
    else:
        return reader

    __logger.debug(
        f"{dataset.short_name} adapted to account for the time offset"
    )

    # Adapt the reader with the exact timestamps
    return TimestampAdapter(reader, **tadapt_kwargs)
