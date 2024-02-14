from pytesmo.validation_framework.metric_calculators_adapters import TsDistributor
from pytesmo.time_series.grouping import YearlessDatetime
from validator.validation.globals import INTRA_ANNUAL_SLICES
from typing import Optional, List, Tuple, Dict
import os
from datetime import datetime
import json
from abc import ABC, abstractmethod


class IntraAnnualSlicesDefault(ABC):
    '''
    Class to load default intra annual slice definitions from the `validator.validation.globals` file.
    Alternatively, the user can provide a custom JSON file containing the definitions.
    Intra annual slice definitions are stored in dictionaries with the following structure:

    {"seasons":
        {"S1": [[12, 1], [2, 28]]      # December 1st to February 28th
        "S2": [[3, 1], [5, 31]]       # March 1st to May 31st
        "S3": [[6, 1], [8, 31]]       # June 1st to August 31st
        "S4": [[9, 1], [11, 30]] }}     # September 1st to November 30th

    These dictionaries will be loaded as properties of the class, so that they can be accessed later on and be treated as the default.

    Parameters
    ----------

    custom_file : str, optional
        JSON File containing the intra annual slice definitions in the same format as in `validator.validation.globals`, by default None. If None, the default as defined in `validator.validation.globals` will be used.

    '''

    def __init__(self, custom_file: Optional[str] = None) -> None:
        self.custom_file = custom_file

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(custom_file={self.custom_file})'

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({os.path.basename(self.custom_file)})'

    def _load_json_data(self, json_path: str) -> dict:
        '''Reads and loads the JSON file into a dictionary.

        Parameters
        ----------
        json_path : str
            Path to the JSON file containing the intra annual slice definitions.

        Returns
        -------
        dict
            Dictionary containing the default intra annual slice definitions.
        '''

        with open(json_path, 'r') as f:
            return json.load(f)

    @abstractmethod
    def _get_available_slices(self):
        pass

class IntraAnnualSlicer(IntraAnnualSlicesDefault):
    '''Class to create custom intra annual slices, based on the default definitions.

    Parameters
    ----------
    intra_annual_slice_type : str
        Type of intra annual slice to be created. Must be one of the available default types. Officially, "months" and "seasons" are implemented. The user can implement their own defaults, though (see `IntraAnnualSlicesDefault`). Default is "months".
    overlap : int, optional
        Number of days to be added/subtracted to the beginning/end of the intra annual slice. Default is 0.
    custom_file : str, optional
        Path to the JSON file containing the intra annual slice definitions, by default None (meaning the defaults as defined in `validator.validation.globals` will be used)
    '''

    def __init__(self,
                 intra_annual_slice_type: Optional[str] = 'months',
                 overlap: Optional[int] = 0,
                 custom_file: Optional[str] = None):
        self.overlap = overlap
        self.intra_annual_slice_type = intra_annual_slice_type
        super().__init__(custom_file=custom_file)

        self.available_slices = self._get_available_slices()
        if not self.available_slices:
            raise FileNotFoundError(
                f'Invalid custom file path. Please provide a valid JSON file containing the intra annual slice definitions.'
            )
        elif self.intra_annual_slice_type not in self.available_slices:
            raise KeyError(
                f'Invalid intra annual slice type. Available types are: {self.available_slices}'
            )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(intra_annual_slice_type={self.intra_annual_slice_type}, overlap={self.overlap})'

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.intra_annual_slice_type}, {self.overlap})'

    def __date_to_doy(self, date_tuple: Tuple[int, int]) -> int:
        '''Converts a date list [month, day] to a day of the year (doy). Leap years are neglected.

        Parameters
        ----------
        date_tuple : List[int]
            List containing the month and day of the date to be converted. The year is not required, as it is not used in the conversion.

        Returns
        -------
        int
            Day of the year (doy) corresponding to the date provided.
        '''

        _doy = YearlessDatetime(date_tuple[0], date_tuple[1]).doy
        if _doy > 60:  # assume NO leap year
            _doy -= 1

        return _doy

    def __doy_to_date(self, doy: int) -> Tuple[int, int]:
        '''Converts a day of the year (doy) to a date tuple (month, day). Leap years are neglected.

        Parameters
        ----------
        doy : int
            Day of the year (doy) to be converted.

        Returns
        -------
        Tuple[int]
            Tuple containing the month and day corresponding to the doy provided.
        '''

        date = datetime.strptime(str(doy), '%j')
        month = date.strftime('%m')
        day = date.strftime('%d')

        return int(month), int(day)

    def __update_date(self, date: Tuple[int, int],
                      overlap_direction: float) -> Tuple[int, int]:
        '''Updates a date tuple (month, day) by adding/subtracting the overlap value to/from it.

        Parameters
        ----------
        date : Tuple[int]
            Date to be updated.
        overlap_direction : float
            Direction of the overlap. Must be either -1 or +1. -1: subtract overlap value from date; +1: add overlap value to date.

        Returns
        -------
        Tuple[int]
            Updated date tuple.
        '''

        overlap_direction = overlap_direction / abs(
            overlap_direction)  # making sure it's either -1 or +1
        _doy = self.__date_to_doy(date)
        _doy += int(overlap_direction * self.overlap)

        if _doy < 1:
            _doy = 365 - abs(_doy)
        elif _doy > 365:
            _doy = _doy - 365

        return self.__doy_to_date(_doy)

    def _custom_intra_annual_slice(self):
        return {
            key: (self.__update_date(val[0], overlap_direction=-1),
                  self.__update_date(val[1], overlap_direction=+1))
            for key, val in self.intra_annual_slices_dict[
                self.intra_annual_slice_type].items()
        }

    def _get_available_slices(self):
        if not self.custom_file:
            self.intra_annual_slices_dict = INTRA_ANNUAL_SLICES
            return list(self.intra_annual_slices_dict.keys())
        elif os.path.isfile(self.custom_file):
            self.intra_annual_slices_dict = self._load_json_data(self.custom_file)
            return list(self.intra_annual_slices_dict.keys())
        else:
            return None

    @property
    def custom_intra_annual_slices(self) -> Dict[str, TsDistributor]:
        '''Custom intra annual slice based, on the default definitions and the overlap value.

        Parameters
        ----------
        None

        Returns
        -------
        dict[str, TsDistributor]
            Dictionary containing the custom intra annual slice definitions.
        '''

        def tsdistributer(_begin_date: Tuple[int],
                          _end_date: Tuple[int]) -> TsDistributor:
            return TsDistributor(yearless_date_ranges=[(YearlessDatetime(
                *_begin_date), YearlessDatetime(*_end_date))])

        return {
            key: tsdistributer(val[0], val[1])
            for key, val in self._custom_intra_annual_slice().items()
        }

    @property
    def names(self) -> List[str]:
        '''Returns the names of the intra annual slices.

        Parameters
        ----------
        None

        Returns
        -------
        List[str]
            List containing the names of the intra annual slices.
        '''

        return list(self._custom_intra_annual_slice().keys())

    @property
    def metadata(self) -> dict:
        '''Returns the metadata of the intra annual slices.

        Parameters
        ----------
        None

        Returns
        -------
        Dict[str, Union[str, List[str]]]
            Dictionary containing the metadata of the intra annual slices.
        '''

        def _date_formatter(_date: Tuple[int, int]) -> str:
            return f'{_date[0]:02d}-{_date[1]:02d}'

        return {
            'Intra annual slice type':
            self.intra_annual_slice_type,
            'Overlap':
            f'{self.overlap} days',
            'Names_Dates [MM-DD]':
            '(MM-DD):' + (', ').join([
                f'{key}: {_date_formatter(val[0])} to {_date_formatter(val[1])}'
                for key, val in self._custom_intra_annual_slice().items()
            ])
        }
