import xarray as xr
import numpy as np
from validator.validation.intra_annual_temp_windows import TemporalSubWindowsCreator
from validator.validation.globals import METRICS, NON_METRICS, METADATA_TEMPLATE, IMPLEMENTED_COMPRESSIONS, ALLOWED_COMPRESSION_LEVELS, INTRA_ANNUAL_METRIC_TEMPLATE, TEMPORAL_SUB_WINDOW_SEPARATOR, DEFAULT_TSW, TEMPORAL_SUB_WINDOW_NC_COORD_NAME
from typing import Any, List, Dict, Optional, Union, Tuple
import os

class Pytesmo2Qa4smResultsTranscriber:
    """
    Transcribes (=converts) the pytesmo results netCDF4 file format to a more user friendly format, that
    is used by QA4SM.

    Parameters
    ----------
    pytesmo_results : str
        Path to results netCDF4 written by `qa4sm.validation.validation.check_and_store_results`, which is in the old `pytesmo` format.
    intra_annual_slices : Union[None, TemporalSubWindowsCreator]
        The temporal sub-windows for the results. Default is None, which means that no temporal sub-windows are
        used, but only the 'bulk'. If an instance of `valdiator.validation.TemporalSubWindowsCreator` is provided,
        the temporal sub-windows are used as provided by the TemporalSubWindowsCreator instance.
    """

    def __init__(self,
                 pytesmo_results: str,
                 intra_annual_slices: Union[None, TemporalSubWindowsCreator] = None):

        self.intra_annual_slices: Union[
            None, TemporalSubWindowsCreator] = intra_annual_slices
        self._temporal_sub_windows: Union[
            None, TemporalSubWindowsCreator] = intra_annual_slices

        self._default_non_metrics: List[str] = NON_METRICS

        self.METADATA_TEMPLATE: Dict[str, Union[None, Dict[str, Union[
            np.ndarray, np.float32, np.array]]]] = METADATA_TEMPLATE

        self.temporal_sub_windows_checker_called: bool = False
        self.only_default_case: bool = True

        self.pytesmo_ncfile = f'{pytesmo_results}'
        if not os.path.isfile(pytesmo_results):
            print(
                f'FileNotFoundError: \n\nFile {pytesmo_results} not found. Please provide a valid path to a pytesmo results netCDF file.'
            )
            self.exists = False
            return None
        else:
            self.exists = True
        with xr.open_dataset(pytesmo_results) as pr:
            self.pytesmo_results: xr.Dataset = pr

        # os.remove(pytesmo_results)
        # os.rename(pytesmo_results, self.pytesmo_ncfile)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(pytesmo_results="{self.pytesmo_ncfile}", intra_annual_slices={self.intra_annual_slices.__repr__()})'

    def __str__(self) -> str:
        return f'{self.__class__.__name__}("{os.path.basename(self.pytesmo_ncfile)}", {self.intra_annual_slices})'

    def temporal_sub_windows_checker(
            self) -> Tuple[bool, Union[List[str], None]]:
        """
        Checks the temporal sub-windows and returns which case of temporal sub-window is used, as well as a list of the
        temporal sub-windows. Keeps track of whether the method has been called before.

        Returns
        -------
        Tuple[bool, Union[List[str], None]]
            A tuple indicating the temporal sub-window type and the list of temporal sub-windows.
            bulk case: (True, [`globals.DEFAULT_TSW`]),
            intra-annual windows case: (False, list of temporal sub-windows)
        """

        self.temporal_sub_windows_checker_called = True
        if self.intra_annual_slices is None:
            return True, [DEFAULT_TSW]
        elif isinstance(self.intra_annual_slices, TemporalSubWindowsCreator):
            self.intra_annual_slices = self.intra_annual_slices.names
            return False, self.intra_annual_slices
        else:
            raise TypeError(
                'intra_annual_slices must be None or an instance of `TemporalSubWindowsCreator`'
            )

    @property
    def non_metrics_list(self) -> List[str]:
        """
            Get the non-metrics from the pytesmo results.

            Returns
            -------
            List[str]
                A list of non-metric names.

            Raises
            ------
            None
            """

        non_metrics_lst = []
        for non_metric in self._default_non_metrics:
            if non_metric in self.pytesmo_results:
                non_metrics_lst.append(non_metric)
            else:
                print(
                    f'Non-metric \'{non_metric}\' not contained in pytesmo results. Skipping...'
                )
                continue
        return non_metrics_lst

    def is_valid_metric_name(self, metric_name):
        """
        Checks if a given metric name is valid, based on the defined `globals.INTRA_ANNUAL_METRIC_TEMPLATE`.

        Parameters:
        metric_name (str): The metric name to be checked.

        Returns:
        bool: True if the metric name is valid, False otherwise.
        """

        valid_prefixes = [
            "".join(
                template.format(tsw=tsw, metric=metric)
                for template in INTRA_ANNUAL_METRIC_TEMPLATE)
            for tsw in self.intra_annual_slices for metric in METRICS
        ]
        return any(metric_name.startswith(prefix) for prefix in valid_prefixes)

    @property
    def metrics_list(self) -> List[str]:
        """Get the metrics dictionary. Whole procedure based on the premise, that metric names of valdiations of intra-annual
        temporal sub-windows are of the form: `metric_long_name = 'intra_annual_window{validator.validation.globals.TEMPORAL_SUB_WINDOW_SEPARATOR}metric_short_name'`. If this is not the
        case, it is assumed the 'bulk' case is present and the metric names are assumed to be the same as the metric
        short names.

        Returns
        -------
        Dict[str, str]
            The metrics dictionary.
        """

        # check if the metric names are of the form: `metric_long_name = 'intra_annual_window{TEMPORAL_SUB_WINDOW_SEPARATOR}metric_short_name'` and if not, assume the 'bulk' case

        _metrics = [
            metric for metric in self.pytesmo_results
            if self.is_valid_metric_name(metric)
        ]

        if len(_metrics) != 0:  # intra-annual case
            return list(set(_metrics))
        else:  # bulk case
            return [
                long for long in self.pytesmo_results
                if long not in self.non_metrics_list
            ]

    def get_pytesmo_attrs(self) -> None:
        """
        Get the attributes of the pytesmo results and add them to the transcribed dataset.
        """
        for attr in self.pytesmo_results.attrs:
            self.transcribed_dataset.attrs[attr] = self.pytesmo_results.attrs[
                attr]

    def trim_n_obs_name(self) -> None:
        """
        Trim the 'n_obs' variable name to 'n_obs' if it's not already named so.
        """

        def get_n_obs_var_name() -> str:
            return [var for var in self.transcribed_dataset
                    if 'n_obs' in var][0]

        if get_n_obs_var_name() != 'n_obs':
            self.transcribed_dataset = self.transcribed_dataset.rename(
                {get_n_obs_var_name(): 'n_obs'})

    def drop_obs_dim(self) -> None:
        """
        Drops the 'obs' dimension from the transcribed dataset, if it exists.
        """
        if 'obs' in self.transcribed_dataset.dims:
            self.transcribed_dataset = self.transcribed_dataset.drop_dims(
                'obs')

    @staticmethod
    def update_dataset_var(ds: xr.Dataset, var: str, coord_key: str,
                           coord_val: str, data_vals: List) -> xr.Dataset:
        """
        Update a variable of given coordinate in the dataset.

        Parameters
        ----------
        ds : xr.Dataset
            The dataset to be updated.
        var : str
            The variable to be updated.
        coord_key : str
            The name of the coordinate of the variable to be updated.
        coord_val : str
            The value of the coordinate of the variable to be updated.
        data_vals : List
            The data to be updated.

        Returns
        -------
        xr.Dataset
            The updated dataset.
        """

        ds[var] = ds[var].copy(
        )  # ugly, but necessary, as xr.Dataset objects are immutable
        ds[var].loc[{coord_key: coord_val}] = data_vals

        return ds

    def get_transcribed_dataset(self) -> xr.Dataset:
        """
        Get the transcribed dataset, containing all metric and non-metric data provided by the pytesmo results. Metadata
        is not yet included.


        Returns
        -------
        xr.Dataset
            The transcribed, metadata-less dataset.
        """
        self.only_default_case, self.intra_annual_slices = self.temporal_sub_windows_checker(
        )

        self.pytesmo_results[
            TEMPORAL_SUB_WINDOW_NC_COORD_NAME] = self.intra_annual_slices

        metric_vars = self.metrics_list
        self.transcribed_dataset = xr.Dataset()

        for var_name in metric_vars:
            new_name = var_name
            if not self.only_default_case:
                _tsw, new_name = new_name.split(TEMPORAL_SUB_WINDOW_SEPARATOR)

            if new_name not in self.transcribed_dataset:
                # takes the data associated with the metric new_name and adds it as a new variabel
                # more precisely, it assigns copies of this data to each temporal sub-window, which is the new dimension
                self.transcribed_dataset[new_name] = self.pytesmo_results[
                    var_name].expand_dims(
                        {
                            TEMPORAL_SUB_WINDOW_NC_COORD_NAME:
                            self.intra_annual_slices
                        },
                        axis=-1)
            else:
                # the variable already exists, but we need to update it with the real data (as opposed to the data of the first temporal sub-window, which is the default behaviour of expand_dims())
                self.transcribed_dataset = Pytesmo2Qa4smResultsTranscriber.update_dataset_var(
                    ds=self.transcribed_dataset,
                    var=new_name,
                    coord_key=TEMPORAL_SUB_WINDOW_NC_COORD_NAME,
                    coord_val=_tsw,
                    data_vals=self.pytesmo_results[var_name].data)

            # Copy attributes from the original variable to the new variable
            self.transcribed_dataset[new_name].attrs = self.pytesmo_results[
                var_name].attrs

        # Add non-metric variables directly
        self.transcribed_dataset = self.transcribed_dataset.merge(
            self.pytesmo_results[self.non_metrics_list])

        self.get_pytesmo_attrs()
        self.trim_n_obs_name()
        self.drop_obs_dim()

        self.transcribed_dataset[
            TEMPORAL_SUB_WINDOW_NC_COORD_NAME].attrs = dict(
                long_name="temporal sub-window",
                standard_name="temporal sub-window",
                units="1",
                valid_range=[0, len(self.intra_annual_slices)],
                axis="T",
                description="temporal sub-window name for the dataset",
                temporal_sub_window_type="No temporal sub-windows used"
                if self.only_default_case is True else
                self._temporal_sub_windows.metadata['Temporal sub-window type'],
                overlap="No temporal sub-windows used"
                if self.only_default_case is True else
                self._temporal_sub_windows.metadata['Overlap'],
                intra_annual_window_definition="No temporal sub-windows used"
                if self.only_default_case is True else
                self._temporal_sub_windows.metadata['Pretty Names [MM-DD]'],
            )

        try:
            _dict = {
                'attr_name': DEFAULT_TSW,
                'attr_value': self._temporal_sub_windows.metadata[DEFAULT_TSW]
            }
            self.transcribed_dataset[
                TEMPORAL_SUB_WINDOW_NC_COORD_NAME].attrs.update(
                    {_dict['attr_name']: _dict['attr_value']})
        except AttributeError:
            pass

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

        os.remove(self.pytesmo_ncfile)
        # os.rename(self.pytesmo_ncfile, self.pytesmo_ncfile + '.old')
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
