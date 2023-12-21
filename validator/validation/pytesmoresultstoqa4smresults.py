import xarray as xr
import numpy as np
from typing import List, Dict, Tuple, Union
import pandas as pd
from validator.validation.intra_annual_slice_maker import IntraAnnualSlicer
from validator.validation.globals import METADATA_TEMPLATE


class Pytesmo2Qa4smResultsTranscriber:
    """
    Transcribes (=converts) the new pytesmo results dictionary format to a more user friendly format, that
    is used by QA4SM.

    Parameters
    ----------
    pytesmo_results : dict
        The pytesmo results dictionary.
    intra_annual_slices : Union[None, IntraAnnualSlicer]
        The intra annual slices for the results. Default is None, which means that no intra-annual intra annual slices are
        used, but only the 'bulk'. If an instance of `valdiator.validation.IntraAnnualSlicer` is provided,
        the intra annual slices are used as provided by the IntraAnnualSlicer instance.
    """

    def __init__(self,
                 pytesmo_results: dict,
                 intra_annual_slices: Union[None, IntraAnnualSlicer] = None):

        self.intra_annual_slices: Union[
            None, IntraAnnualSlicer] = intra_annual_slices
        self._intra_annual_slices: Union[
            None, IntraAnnualSlicer] = intra_annual_slices

        self._default_non_metrics: List[str] = [
            'gpi', 'lon', 'lat', 'clay_fraction', 'climate_KG',
            'climate_insitu', 'elevation', 'instrument', 'latitude', 'lc_2000',
            'lc_2005', 'lc_2010', 'lc_insitu', 'longitude', 'network',
            'organic_carbon', 'sand_fraction', 'saturation', 'silt_fraction',
            'station', 'timerange_from', 'timerange_to', 'variable',
            'instrument_depthfrom', 'instrument_depthto', 'frm_class'
        ]

        # self.METADATA_TEMPLATE: Dict[str, Union[None, Dict[str, Union[
        #     np.ndarray, np.float32, np.array]]]] = {
        #         'other_ref': None,
        #         'ismn_ref': {
        #             'clay_fraction': np.float32([np.nan]),
        #             'climate_KG': np.array([' ' * 256]),
        #             'climate_insitu': np.array([' ' * 256]),
        #             'elevation': np.float32([np.nan]),
        #             'instrument': np.array([' ' * 256]),
        #             'latitude': np.float32([np.nan]),
        #             'lc_2000': np.float32([np.nan]),
        #             'lc_2005': np.float32([np.nan]),
        #             'lc_2010': np.float32([np.nan]),
        #             'lc_insitu': np.array([' ' * 256]),
        #             'longitude': np.float32([np.nan]),
        #             'network': np.array([' ' * 256]),
        #             'organic_carbon': np.float32([np.nan]),
        #             'sand_fraction': np.float32([np.nan]),
        #             'saturation': np.float32([np.nan]),
        #             'silt_fraction': np.float32([np.nan]),
        #             'station': np.array([' ' * 256]),
        #             'timerange_from': np.array([' ' * 256]),
        #             'timerange_to': np.array([' ' * 256]),
        #             'variable': np.array([' ' * 256]),
        #             'instrument_depthfrom': np.float32([np.nan]),
        #             'instrument_depthto': np.float32([np.nan]),
        #             'frm_class': np.array([' ' * 256]),
        #         }
        #     }

        self.intra_annual_slices_checker_called: bool = False
        self.intra_annual_slices_check: bool = False

        self.pytesmo_results: dict = list(
            self._pytesmo_to_qa4sm_results(pytesmo_results).values())[0]

        self.__lat_arr: np.ndarray = np.array(self.non_metrics['lat']['data'],
                                              dtype=np.float32)
        self.__lon_arr: np.ndarray = np.array(self.non_metrics['lon']['data'],
                                              dtype=np.float32)
        self.__idx_arr: np.ndarray = np.arange(len(self.__lat_arr),
                                               dtype=np.int32)

    def intra_annual_slices_checker(
            self) -> Tuple[bool, Union[List[str], None]]:
        """
        Checks the intra annual slices and returns which case of intra annual slice is used, as well as a list of the
        intra annual slices. Keeps track of whether the method has been called before.

        Returns
        -------
        Tuple[bool, Union[List[str], None]]
            A tuple indicating the intra annual slice type and the list of intra annual slices.
            bulk case: (False, ['bulk']),
            intra-annual windows case: (True, list of intra annual slices)
        """

        self.intra_annual_slices_checker_called = True
        if self.intra_annual_slices is None:
            return False, ['bulk']
        elif isinstance(self.intra_annual_slices, IntraAnnualSlicer):
            self.intra_annual_slices = self.intra_annual_slices.names
            return True, self.intra_annual_slices
        else:
            raise TypeError(
                'intra_annual_slices must be None or an instance of IntraAnnualSlicer'
            )

    def _pytesmo_to_qa4sm_results(self, results: dict) -> dict:
        """
        Converts the new pytesmo results dictionary format to the old format that
        is still used by QA4SM.

        Parameters
        ----------
        results : dict
            Each key in the dictionary is a tuple of ``((ds1, col1), (d2, col2))``,
            and the values contain the respective results for this combination of
            datasets/columns.

        Returns
        -------
        qa4sm_results : dict
            Dictionary in the format required by QA4SM. This involves merging the
            different dictionary entries from `results` to a single dictionary and
            renaming the metrics to avoid name clashes, using the naming convention
            from the old metric calculators.
        """
        # each key is a tuple of ((ds1, col1), (ds2, col2))
        # this adds all tuples to a single list, and then only
        # keeps unique entries
        qa4sm_key = tuple(sorted(set(sum(map(list, results.keys()), []))))

        qa4sm_res = {qa4sm_key: {}}
        for key in results:
            for metric in results[key]:
                # static 'metrics' (e.g. metadata, geoinfo) are not related to datasets
                statics = ["gpi", "n_obs", "lat", "lon"]
                statics.extend(METADATA_TEMPLATE["ismn_ref"])
                if metric in statics:
                    new_key = metric
                else:
                    datasets = list(map(lambda t: t[0], key))
                    if isinstance(metric, tuple):
                        # happens only for triple collocation metrics, where the
                        # metric key is a tuple of (metric, dataset)
                        if metric[1].startswith("0-"):
                            # triple collocation metrics for the reference should
                            # not show up in the results
                            continue
                        new_metric = "_".join(metric)
                    else:
                        new_metric = metric
                    new_key = f"{new_metric}_between_{'_and_'.join(datasets)}"
                qa4sm_res[qa4sm_key][new_key] = results[key][metric]
        return qa4sm_res

    @property
    def non_metrics(self) -> Dict[str, Dict[str, Union[np.ndarray, type]]]:
        """
        Get the non-metrics from the pytesmo results.

        Returns
        -------
        Dict[str, Dict[str, Union[np.ndarray, type]]]
            The non-metrics.
        """
        return {
            key: {
                'data': val,
                'dtype': type(val[0])
            }
            for key, val in self.pytesmo_results.items()
            if key in self._default_non_metrics
        }

    @property
    def metrics_dict(self) -> Dict[str, str]:
        """
        Get the metrics dictionary. Whole procedure based on the premise, that metric names of valdiations of intra-annual
        intra annual slices are of the form: `metric_long_name = 'intra_annual_slice|metric_short_name'`. If this is not the
        case, it is assumed the 'bulk' case is present and the metric names are assumed to be the same as the metric
        short names.

        Returns
        -------
        Dict[str, str]
            The metrics dictionary.
        """
        _metrics = [
            key.split('|')[1] for key in self.pytesmo_results.keys()
            if '|' in key
        ]
        if len(_metrics) != 0:  # bulk case
            return {long: long for long in set(_metrics)}
        else:  # intra-annual case
            return {
                long: long
                for long in self.pytesmo_results.keys()
                if long not in self.non_metrics.keys()
            }

    def get_sorted_metric_precursor(self) -> Dict[str, Dict[str, np.array]]:
        """
        Creates a precursor dictionary of sorted metrics, based on the pytesmo results and later on used to construct
        the metric data dictionary. The sorting is done according to the provided intra annual slices.

        Returns
        -------
        Dict[str, Dict[str, np.array]]
            The sorted dictionary.
        """
        if self.intra_annual_slices_checker_called is False:
            self.intra_annual_slices_check, self.intra_annual_slices = self.intra_annual_slices_checker(
            )

        if self.intra_annual_slices_check is False:
            self.sorted_metric_precursor = {
                intra_annual_slice: {
                    metric_short: self.pytesmo_results[f'{metric_long}']
                    for metric_long, metric_short in self.metrics_dict.items(
                    )  #! check if metric_long and metric_short aren't the same anyhow and if self.metrics_dict is needed
                }
                for intra_annual_slice in self.intra_annual_slices
            }

        elif self.intra_annual_slices_check is True:
            self.sorted_metric_precursor = {
                intra_annual_slice: {
                    metric_short:
                    self.pytesmo_results[f'{intra_annual_slice}|{metric_long}']
                    for metric_long, metric_short in self.metrics_dict.items()
                }
                for intra_annual_slice in self.intra_annual_slices
            }

        else:
            raise TypeError(
                'intra_annual_slices must be None or a list of strings')

        return self.sorted_metric_precursor

    @property
    def metric_data_dict(self) -> Dict[str, xr.DataArray]:
        """
        Get the metric data dictionary. In general, metric data is always a function of location of the spatial
        reference point and of the intra annual slice used. The metric data dictionary is a dictionary of xarray.DataArrays,
        containing the metric data for each intra annual slice.

        Returns
        -------
        Dict[str, xr.DataArray]
            The metric data dictionary. `Keys` are the (short name) metrics and `vals` xarray.DataArrays, containing all
            data of the corresponding metric for each intra annual slice .
        """
        if self.intra_annual_slices_checker_called is False:
            self.intra_annual_slices_check, self.intra_annual_slices = self.intra_annual_slices_checker(
            )

        return {
            metric_short:
            xr.DataArray(np.array([
                self.get_sorted_metric_precursor()[intra_annual_slice]
                [metric_short]
                for intra_annual_slice in self.intra_annual_slices
            ]),
                         dims=('ias', 'idx'),
                         coords={
                             'ias': self.intra_annual_slices,
                             'idx': self.__idx_arr,
                         })
            for metric_short in self.metrics_dict.values()
        }

    @property
    def non_metric_data_dict(self) -> Dict[str, xr.DataArray]:
        """
        Get the non-metric data dictionary. In general, non-metric data is always *only* a function of location of the
        spatial reference point. The non-metric data dictionary is a dictionary of xarray.DataArrays, containing the
        non-metric data for each spatial reference point.

        Returns
        -------
        Dict[str, xr.DataArray]
            The non-metric data dictionary. `Keys` are the non-metrics and `vals` xarray.DataArrays, containing all
            data of the corresponding non-metric for each spatial reference point.
        """
        non_metric_data = {
            non_metric: self.non_metrics[non_metric]['data']
            for non_metric in self.non_metrics
        }

        non_metric_dtypes = {
            non_metric: self.non_metrics[non_metric]['dtype']
            for non_metric in self.non_metrics
        }

        non_metric_df = pd.DataFrame(non_metric_data)
        for non_metric, dtype in non_metric_dtypes.items():
            non_metric_df[non_metric] = non_metric_df[non_metric].astype(dtype)

        return {
            non_metric:
            xr.DataArray(non_metric_df[non_metric].values.T,
                         dims=('idx', ),
                         coords={'idx': self.__idx_arr},
                         name=non_metric)
            for non_metric in non_metric_df.columns
        }

    def set_coordinate_attrs(self) -> None:
        """
        Set the attributes of the coordinates.
        """

        self.transcribed_dataset['lon'].attrs = dict(
            long_name="location longitude",
            standard_name="longitude",
            units="degrees_east",
            valid_range=np.array([-180, 180]),
            axis="X",
            description="Longitude values for the dataset")

        self.transcribed_dataset['lat'].attrs = dict(
            long_name="location latitude",
            standard_name="latitude",
            units="degrees_north",
            valid_range=np.array([-90, 90]),
            axis="Y",
            description="Latitude values for the dataset")

        self.transcribed_dataset['idx'].attrs = dict(
            long_name="location index",
            standard_name="index",
            units="1",
            valid_range=np.array([0, len(self.__idx_arr)]),
            axis="Z",
            description="Index values for the dataset")

        self.transcribed_dataset['ias'].attrs = dict(
            long_name="intra annual slice",
            standard_name="intra annual slice",
            units="1",
            valid_range=np.array([0, len(self.intra_annual_slices)]),
            axis="T",
            description="Intra annual slice name for the dataset",
            intra_annual_slice_type="No intra annual slices used"
            if self.intra_annual_slices_check is False else
            self._intra_annual_slices.metadata['Intra annual slice type'],
            overlap="No intra annual slices used"
            if self.intra_annual_slices_check is False else
            self._intra_annual_slices.metadata['Overlap'],
            intra_annual_slice_definition="No intra annual slices used"
            if self.intra_annual_slices_check is False else
            self._intra_annual_slices.metadata['Names_Dates [MM-DD]'],
        )

    def get_transcribed_dataset(
        self,
        write_to_ncfile: bool = False,
        path: str = None
    ) -> xr.Dataset:  #! remove option to write to ncfile, as metadata still missing
        """
        Get the transcribed dataset, containing all metric and non-metric data provided by the pytesmo results. Metadata
        is not yet included.

        Parameters
        ----------
        write_to_ncfile : bool, optional
            Whether to write the dataset to a NetCDF file, by default False
        path : str, optional
            The path to write the NetCDF file, by default None

        Returns
        -------
        xr.Dataset
            The transcribed, metadata-less dataset.
        """
        self.transcribed_dataset = xr.Dataset(self.metric_data_dict)

        self.transcribed_dataset = xr.merge(
            [self.transcribed_dataset, *self.non_metric_data_dict.values()])

        self.transcribed_dataset = self.transcribed_dataset.assign_coords(
            lat=self.__lat_arr, lon=self.__lon_arr, idx=self.__idx_arr)

        self.set_coordinate_attrs()

        if write_to_ncfile is True:
            self.transcribed_dataset.to_netcdf(path)

        return self.transcribed_dataset
