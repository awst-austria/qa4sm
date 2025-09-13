import logging
from os import path
import numpy as np

from ascat.read_native.cdr import AscatGriddedNcTs
from c3s_sm.interface import C3STs
from ecmwf_models.interface import ERATs
from esa_cci_sm.interface import CCITs
from gldas.interface import GLDASTs
from ismn.interface import ISMN_Interface
from ismn.custom import CustomSensorMetadataCsv
from smap_io.interface import SMAPTs, SMAPL3_V9Reader
from smos.interface import SMOSTs
from pynetcf.time_series import GriddedNcTs, GriddedNcIndexedRaggedTs
from pygeogrids.netcdf import load_grid

from qa4sm_preprocessing.cgls_hr_ssm_swi.reader import S1CglsTs
from qa4sm_preprocessing.reading import GriddedNcOrthoMultiTs, \
    GriddedNcContiguousRaggedTs

from validator.validation import globals
from validator.validation.util import first_file_in

from pytesmo.validation_framework.adapters import TimestampAdapter, \
    BasicAdapter
from validator.models import UserDatasetFile
import pandas as pd

__logger = logging.getLogger(__name__)


class ReaderWithTsExtension:
    """
    Concatenate 2 time series upon reading
    """

    def __init__(self, cls, path, path_ext, *args, **kwargs):
        """
        Parameters
        ----------
        cls: Callable
            Reader class to wrap
        path: str
            Path to the main time series (not the extension dataset)
        path_ext: str
            Extension time series path
        args, kwargs:
            Additional arguments to set up the readers
        """
        self.base_reader = cls(path, *args, **kwargs)
        try:
            self.ext_reader = cls(path_ext, *args, **kwargs)
        except FileNotFoundError:
            logging.error(f"No extension dataset found in path {path_ext}")
            self.ext_reader = None

    @property
    def grid(self):
        return self.base_reader.grid

    def read(self, *args, **kwargs) -> pd.DataFrame:
        """
        Read time series at location for both the base dataset and the
        extension. If extension is read, concatenate both in time.
        """
        ts = self.base_reader.read(*args, **kwargs)
        try:
            if self.ext_reader is not None:
                ext = self.ext_reader.read(*args, **kwargs)
                ts = pd.concat([ts, ext], axis=0)
                ts = ts[~ts.index.duplicated(keep='last')]  # prefer ext. data
        except Exception as e:
            logging.error(f"Extension reading failed for {args} {kwargs} with"
                          f"error: {e}")

        return ts


class SBPCAReader(GriddedNcOrthoMultiTs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self, *args, **kwargs) -> pd.DataFrame:
        ts = super().read(*args, **kwargs)
        if (ts is not None) and not ts.empty:
            ts = ts[ts.index.notnull()]
            for col in ['Chi_2_P', 'M_AVA0', 'N_RFI_X', 'N_RFI_Y', 'RFI_Prob',
                        'Science_Flags']:
                if col in ts.columns:
                    ts[col] = ts[col].fillna(0)
            if 'Soil_Moisture' in ts.columns:
                ts = ts.dropna(subset='Soil_Moisture')
            if 'acquisition_time' in ts.columns:
                ts = ts.dropna(subset='acquisition_time')
        return ts


class SMOSL2Reader(GriddedNcIndexedRaggedTs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self, *args, **kwargs) -> pd.DataFrame:
        ts = super().read(*args, **kwargs)
        if (ts is not None) and not ts.empty:
            ts = ts[ts.index.notnull()]
            for col in ['Chi_2_P', 'M_AVA0', 'N_RFI_X', 'N_RFI_Y', 'RFI_Prob',
                        'Science_Flags']:
                if col in ts.columns:
                    ts[col] = ts[col].fillna(0)
            if 'Soil_Moisture' in ts.columns:
                ts = ts.dropna(subset='Soil_Moisture')
            if 'acquisition_time' in ts.columns:
                ts = ts.dropna(subset='acquisition_time')
        return ts


# class SMAPL3_V9Reader(GriddedNcIndexedRaggedTs):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def read(self, *args, **kwargs) -> pd.DataFrame:
#         ts = super().read(*args, **kwargs)
#         if (ts is not None) and not ts.empty:
#             ts = ts[ts.index.notnull()]
#             for col in ['soil_moisture_error', "retrieval_qual_flag",
#             "freeze_thaw_fraction", "surface_flag",
#                         "surface_temperature", "vegetation_opacity",
#                         "vegetation_water_content", "landcover_class",
#                         'static_water_body_fraction']:
#                 if col in ts.columns:
#                     ts[col] = ts[col].fillna(0)
#             if 'soil_moisture' in ts.columns:
#                 ts = ts.dropna(subset='soil_moisture')
#         assert ts is not None, "No data read"
#         return ts


def create_reader(dataset, version) -> GriddedNcTs:
    """
    Create basic readers (without any adapters / filters) for a dataset version
    """

    reader = None  # reader class, inherits pynetcf time series module

    folder_name = path.join(dataset.storage_path, version.short_name)
    ext_folder_name = path.join(dataset.storage_path,
                                version.short_name + '-ext', 'timeseries')

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
        c3s_data_folder = path.join(folder_name, 'TCDR', '063_images_to_ts',
                                    'combined-daily')
        reader = ReaderWithTsExtension(C3STs, c3s_data_folder, ext_folder_name,
                                       ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.C3SA:
        c3s_data_folder = path.join(folder_name, 'cdr_active_daily')
        reader = ReaderWithTsExtension(C3STs, c3s_data_folder, ext_folder_name,
                                       ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.C3SP:
        c3s_data_folder = path.join(folder_name, 'cdr_passive_daily')
        reader = ReaderWithTsExtension(C3STs, c3s_data_folder, ext_folder_name,
                                       ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.C3S_RZSM:
        c3s_data_folder = path.join(folder_name, 'cdr_rzsm_daily')
        reader = ReaderWithTsExtension(C3STs, c3s_data_folder, ext_folder_name,
                                       ioclass_kws={'read_bulk': True})

    if (dataset.short_name == globals.CCIC or
            dataset.short_name == globals.CCIA or
            dataset.short_name == globals.CCIP or
            dataset.short_name == globals.CCI_RZSM):
        reader = CCITs(folder_name, ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.GLDAS:
        reader = GLDASTs(folder_name, ioclass_kws={'read_bulk': True})

    if (dataset.short_name == globals.SMAP_L3 and version.short_name !=
            'SMAP_V9_AM_PM'):
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
        reader = ReaderWithTsExtension(ERATs, folder_name, ext_folder_name,
                                       ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.ERA5_LAND:
        reader = ReaderWithTsExtension(ERATs, folder_name, ext_folder_name,
                                       ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.CGLS_SCATSAR_SWI1km:
        reader = S1CglsTs(folder_name)

    if dataset.short_name == globals.CGLS_CSAR_SSM1km:
        reader = S1CglsTs(folder_name)

    if dataset.short_name == globals.SMOS_L3:
        reader = SMOSTs(folder_name, ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.SMOS_L2:
        reader = ReaderWithTsExtension(
            SMOSL2Reader, folder_name, ext_folder_name,
            ioclass_kws={'read_bulk': True},
            grid=load_grid(path.join(folder_name, "grid.nc"))
        )

    if dataset.short_name == globals.SMAP_L2:
        reader = GriddedNcOrthoMultiTs(folder_name,
                                       ioclass_kws={'read_bulk': True})

    if (dataset.short_name == globals.SMAP_L3 and version.short_name ==
            'SMAP_V9_AM_PM'):
        smap_data_folder = path.join(folder_name, 'netcdf')
        reader = SMAPL3_V9Reader(smap_data_folder,
                                 ioclass_kws={'read_bulk': True})

    if dataset.short_name == globals.SMOS_SBPCA:
        if version.short_name == globals.SMOS_SBPCA_v724:
            reader = SBPCAReader(folder_name, ioclass_kws={'read_bulk': True})
        elif version.short_name == globals.V781_FinalMetrics:
            reader = SMOSL2Reader(folder_name,
                                  grid=load_grid(
                                      path.join(folder_name, "grid.nc")),
                                  ioclass_kws={'read_bulk': True})
        else:
            raise NotImplementedError("Unknown version of SMOS_DPGS_RC_L2SM")

    if dataset.user and len(dataset.user_dataset.all()):
        file = UserDatasetFile.objects.get(dataset=dataset)
        if file.file_name.endswith('nc') or file.file_name.endswith('nc4'):
            reader = GriddedNcOrthoMultiTs(
                file.get_raw_file_path + "/timeseries",
                ioclass_kws={'read_bulk': True})
        elif file.file_name.endswith('zip'):
            reader = GriddedNcContiguousRaggedTs(
                file.get_raw_file_path + "/timeseries",
                ioclass_kws={'read_bulk': True})

    if not reader:
        raise ValueError(
            "Reader for dataset '{}' not available".format(dataset))

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

    elif ((dataset.short_name == globals.SMOS_SBPCA) and
          (version.short_name == globals.SMOS_SBPCA_v724)):
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

    # No adaptation needed
    else:
        return reader

    __logger.debug(
        f"{dataset.short_name} adapted to account for the time offset"
    )

    # Adapt the reader with the exact timestamps
    return TimestampAdapter(reader, **tadapt_kwargs)
