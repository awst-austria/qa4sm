import xarray as xr
import numpy as np
from validator.validation.intra_annual_slicer import IntraAnnualSlicer
from validator.validation.globals import NON_METRICS, METADATA_TEMPLATE, IMPLEMENTED_COMPRESSIONS, ALLOWED_COMPRESSION_LEVELS, INTRA_ANNUAL_METRIC_TEMPLATE, INTRA_ANNUAL_SEPARATOR
from typing import Any, List, Dict, Optional, Union, Tuple
import pandas as pd
import os


class Pytesmo2Qa4smResultsTranscriber:
    """
    Transcribes (=converts) the pytesmo results netCDF4 file format to a more user friendly format, that
    is used by QA4SM.

    Parameters
    ----------
    pytesmo_results : str
        Path to results netCDF4 written by `qa4sm.validation.validation.check_and_store_results`, which is in the old `pytesmo` format.
    intra_annual_slices : Union[None, IntraAnnualSlicer]
        The intra annual slices for the results. Default is None, which means that no intra-annual intra annual slices are
        used, but only the 'bulk'. If an instance of `valdiator.validation.IntraAnnualSlicer` is provided,
        the intra annual slices are used as provided by the IntraAnnualSlicer instance.
    """

    def __init__(self,
                 pytesmo_results: str,
                 intra_annual_slices: Union[None, IntraAnnualSlicer] = None):

        self.intra_annual_slices: Union[
            None, IntraAnnualSlicer] = intra_annual_slices
        self._intra_annual_slices: Union[
            None, IntraAnnualSlicer] = intra_annual_slices

        self._default_non_metrics: List[str] = NON_METRICS

        self.METADATA_TEMPLATE: Dict[str, Union[None, Dict[str, Union[
            np.ndarray, np.float32, np.array]]]] = METADATA_TEMPLATE

        self.intra_annual_slices_checker_called: bool = False
        self.intra_annual_slices_check: bool = False

        with xr.open_dataset(pytesmo_results) as pr:
            self.pytesmo_results: xr.Dataset = pr

        self.pytesmo_ncfile = f'{pytesmo_results}'
        # os.remove(pytesmo_results)
        # os.rename(pytesmo_results, self.pytesmo_ncfile)

        self.__lat_arr: np.ndarray = np.array(self.non_metrics['lat']['data'],
                                              dtype=np.float32)
        self.__lon_arr: np.ndarray = np.array(self.non_metrics['lon']['data'],
                                              dtype=np.float32)
        self.__idx_arr: np.ndarray = np.arange(len(self.__lat_arr),
                                               dtype=np.int32)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(pytesmo_results="{self.pytesmo_ncfile}", intra_annual_slices={self.intra_annual_slices.__repr__()})'

    def __str__(self) -> str:
        return f'{self.__class__.__name__}("{os.path.basename(self.pytesmo_ncfile)}", {self.intra_annual_slices})'

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
                'intra_annual_slices must be None or an instance of `IntraAnnualSlicer`'
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
                statics.extend(self.METADATA_TEMPLATE["ismn_ref"])
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
            non_metric: {
                'data': self.pytesmo_results[non_metric].values,
                'dtype': self.pytesmo_results[non_metric].dtype
            }
            for non_metric in self._default_non_metrics
        }

    @property
    def metrics_dict(self) -> Dict[str, str]:
        """Get the metrics dictionary. Whole procedure based on the premise, that metric names of valdiations of intra-annual
        intra annual slices are of the form: `metric_long_name = 'intra_annual_slice{validator.validation.globals.INTRA_ANNUAL_SEPARATOR}metric_short_name'`. If this is not the
        case, it is assumed the 'bulk' case is present and the metric names are assumed to be the same as the metric
        short names.

        Returns
        -------
        Dict[str, str]
            The metrics dictionary.
        """
        _metrics = [
            metric.split(INTRA_ANNUAL_SEPARATOR)[1]
            for metric in self.pytesmo_results
            if INTRA_ANNUAL_SEPARATOR in metric
        ]
        if len(
                _metrics
        ) != 0:  # bulk case             #? check if this is the best way to check for bulk case
            return {long: long for long in set(_metrics)}
        else:  # intra-annual case
            return {
                long: long
                for long in self.pytesmo_results
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
                    self.pytesmo_results[''.join(
                        INTRA_ANNUAL_METRIC_TEMPLATE).format(
                            temp_slice=intra_annual_slice, metric=metric_long)]
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
                         dims=('temp_slice', 'idx'),
                         coords={
                             'temp_slice': self.intra_annual_slices,
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

        self.transcribed_dataset['temp_slice'].attrs = dict(
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

    def get_pytesmo_attrs(self) -> None:
        for attr in self.pytesmo_results.attrs:
            self.transcribed_dataset.attrs[attr] = self.pytesmo_results.attrs[
                attr]

    def get_transcribed_dataset(self) -> xr.Dataset:
        """
        Get the transcribed dataset, containing all metric and non-metric data provided by the pytesmo results. Metadata
        is not yet included.


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
        self.get_pytesmo_attrs()

        return self.transcribed_dataset

    def build_outname(self, root: str, keys: List[Tuple[str]]) -> str:
        """
        Build the output name for the NetCDF file. Slight alteration of the original function from pytesmo
        `pytesmo.validation_framework.results_manager.build_filename`.

        Parameters
        ----------
        root : str
            The root path, where the file is to be written to.
        keys : List[Tuple[str]]
            The keys of the pytesmo results.

        Returns
        -------
        str
            The output name for the NetCDF file.

        """

        ds_names = []
        for key in keys:
            for ds in key:
                if isinstance(ds, tuple):
                    ds_names.append(".".join(list(ds)))
                else:
                    ds_names.append(ds)

        fname = "_with_".join(ds_names)
        ext = "nc"
        if len(os.path.join(root, ".".join([fname, ext]))) > 255:
            ds_names = [str(ds[0]) for ds in key]
            fname = "_with_".join(ds_names)

            if len(os.path.join(root, ".".join([fname, ext]))) > 255:
                fname = "validation"
        self.outname = os.path.join(root, ".".join([fname, ext]))
        return self.outname

    def write_to_netcdf(self,
                        path: str,
                        mode: Optional[str] = 'w',
                        format: Optional[str] = 'NETCDF4',
                        engine: Optional[str] = 'netcdf4',
                        encoding: Optional[dict] = {
                            "zlib": True,
                            "complevel": 5
                        },
                        compute: Optional[bool] = True,
                        **kwargs) -> str:
        """
        Write the transcribed dataset to a NetCDF file, based on `xarray.Dataset.to_netcdf`

        Parameters
        ----------
        path : str
            The path to write the NetCDF file
        mode : Optional[str], optional
            The mode to open the NetCDF file, by default 'w'
        format : Optional[str], optional
            The format of the NetCDF file, by default 'NETCDF4'
        engine : Optional[str], optional
            The engine to use, by default 'netcdf4'
        encoding : Optional[dict], optional
            The encoding to use, by default {"zlib": True, "complevel": 5}
        compute : Optional[bool], optional
            Whether to compute the dataset, by default True
        **kwargs : dict
            Keyword arguments passed to `xarray.Dataset.to_netcdf`.

        Returns
        -------
        str
            The path to the NetCDF file.

        """

        # os.remove(self.pytesmo_ncfile)
        os.rename(self.pytesmo_ncfile, self.pytesmo_ncfile + '.old')
        self.transcribed_dataset.to_netcdf(path, mode, **kwargs)

        return path

    def compress(self,
                 path: str,
                 compression: str = 'zlib',
                 complevel: int = 5) -> None:
        """
        Opens the generated results netCDF file and writes to a new netCDF file with new compression parameters. The smaller of both files is then deleted and the remainign one named according to the original file.

        Parameters
        ----------
        fpath: str
            Path to the netCDF file to be re-compressed.
        compression: str
            Compression algorithm to be used. Currently only 'zlib' is implemented.
        complevel: int
            Compression level to be used. The higher the level, the better the compression, but the longer it takes.

        Returns
        -------
        None
        """

        if compression in IMPLEMENTED_COMPRESSIONS and complevel in ALLOWED_COMPRESSION_LEVELS:

            def encoding_params(ds: xr.Dataset, compression: str,
                                complevel: int) -> dict:
                return {
                    str(var): {
                        compression: True,
                        'complevel': complevel
                    }
                    for var in ds.variables
                    if not np.issubdtype(ds[var].dtype, np.object_)
                }

            try:
                with xr.open_dataset(path) as ds:
                    parent_dir, file = os.path.split(path)
                    re_name = os.path.join(parent_dir, f're_{file}')
                    ds.to_netcdf(re_name,
                                 mode='w',
                                 format='NETCDF4',
                                 encoding=encoding_params(
                                     ds, compression, complevel))
                    print(f'\n\nRe-compression finished\n\n')

                # for small initial files, the re-compressed file might be larger than the original
                # delete the larger file and keep the smaller; rename the smaller file to the original name if necessary
                fpath_size = os.path.getsize(path)
                re_name_size = os.path.getsize(re_name)

                if fpath_size < re_name_size:
                    os.remove(re_name)
                else:
                    os.remove(path)
                    os.rename(re_name, path)

            except Exception as e:
                print(
                    f'\n\nRe-compression failed. {e}\nContinue without re-compression.\n\n'
                )
                os.remove(re_name) if os.path.exists(re_name) else None

        else:
            print(
                f'\n\nRe-compression failed. Compression has to be {IMPLEMENTED_COMPRESSIONS} and compression levels other than {ALLOWED_COMPRESSION_LEVELS} are not supported. Continue without re-compression.\n\n'
            )
