import logging
from typing import List, Union

import numpy as np
import pandas as pd

from pytesmo.validation_framework.adapters import AdvancedMaskingAdapter, \
    BasicAdapter, ColumnCombineAdapter
from ismn.interface import ISMN_Interface
from re import sub as regex_sub

__logger = logging.getLogger(__name__)

'''
Bitmask filter for SMOS, you can only exclude data on set bits (not on unset 
bits)
'''


def smos_exclude_bitmask(data, bitmask):
    """
    Returns boolean iterable of the same size as 'data', where False
    indicates that the value is flagged according to the given bitmask

    For a value in 'data' to be flagged, the function bit(value) should return
    exactly 'bitmask'

    Parameters
    ----------
    data: pd.Series
        Data with the flag values
    bitmask: int
        in of type e.g. 0b0001

    Returns
    -------
    mask: np.array
        array of booleans
    """
    thedata = data

    if type(thedata) is pd.Series:
        thedata = thedata.values

    mask = (thedata & bitmask) != bitmask
    return mask


def check_normalized_bits_array(
        numbers: Union[pd.Series, np.ndarray],
        bit_indices: List[list]
) -> bool:
    """
    Takes a list of bit_indices ([0] is the first bit only, [0,1] are the first
    two bits) and a number and checks if the bit(s) is (are) active for this
    number.

    If multiple combinations are passed in bit_indices, ANY of them
    must be fulfilled.

    Parameters
    ----------
    numbers: pd.Series or np.array
        Numbers (integer) for which we compare the bits to the passed ones.
    bit_indices: list of lists
        A list of bit indices that are checked. Each sub list is a bit
        combination that is compared to the number
        e.g [[0]] means the 1st bit only must be active, e.g. 0b1 or 0b101
            (for the passed number in bin format).
        e.g [[0],[1]] means that 1st OR 2nd bit must be active e.g. 0b01 or
        0b10
        e.g [[0, 1]] means that the first AND second bit must be active: 0b11
        e.g [[2],[0,1]] mean that the (3rd OR (1st AND 2nd)) must be active
            e.g. True for 0b100, 0b1011 etc.
    Returns
    -------
    flags: np.array
        Whether the passed bits fulfilled were active in the passed numbers.
        boolean array of the same shape as the input numbers array.
        In this array, False indicates a value that should not be kept (i.e.
        a flagged value)
    """
    if type(numbers) is pd.Series:
        numbers = numbers.values

    # Make sure the correct format is passed
    numbers = numbers.astype(int)

    return ~np.any(
        np.array([
            np.all(
                np.array([(numbers >> i) & 1 for i in bit_index]),
                axis=0)
            for bit_index in bit_indices]),
        axis=0)


'''
Get the variables that need to be loaded for filtering the data on them.
'''


def get_used_variables(filters, dataset, variable):
    variables = [variable.short_name]

    if not filters:
        return variables

    try:
        for fil in filters:
            if fil.name == "FIL_ISMN_GOOD":
                variables.append('soil_moisture_flag')
                continue

            if ((fil.name == "FIL_C3S_FLAG_0") or
                    (fil.name == "FIL_C3S_NO_FLAG_1") or
                    (fil.name == "FIL_C3S_NO_FLAG_2")):
                variables.append('flag')
                continue

            if ((fil.name == "FIL_C3S_MODE_ASC") or
                    (fil.name == "FIL_C3S_MODE_DESC")):
                variables.append('mode')
                continue

            if fil.name == "FIL_GLDAS_UNFROZEN":
                temp_variable = variable.short_name.replace("Moi", "TMP")
                variables.append(temp_variable)
                variables.append('SWE_inst')
                continue

            if fil.name in ["FIL_ASCAT_METOP_A", "FIL_ASCAT_METOP_B",
                            "FIL_ASCAT_METOP_C"]:
                variables.append('sat_id')
                continue

            if fil.name == "FIL_ASCAT_UNFROZEN_UNKNOWN" and dataset:
                variables.append('ssf')
                continue

            if fil.name == "FIL_ASCAT_UNFROZEN_UNKNOWN_new" and dataset:
                variables.append('surface_flag')

            if fil.name == "FIL_ASCAT_NO_CONF_FLAGS":
                variables.append('conf_flag')
                continue

            if fil.name == "FIL_ASCAT_NO_PROC_FLAGS":
                variables.append('proc_flag')
                continue

            if fil.name == "FIL_ASCAT_NO_PROC_FLAGS_new":
                variables.append('processing_flag')
                continue

            if fil.name == "FIL_SMOS_QUAL_RECOMMENDED":
                variables.append('Quality_Flag')
                continue

            if fil.name == "FIL_SMOS_UNFROZEN":
                variables.append('Scene_Flags')
                variables.append('Soil_Temperature_Level1')
                continue

            if fil.name == "FIL_SMOS_UNPOLLUTED":
                variables.append('Scene_Flags')
                continue

            if fil.name == "FIL_SMOS_BRIGHTNESS":
                variables.append('Processing_Flags')
                continue

            if fil.name == "FIL_SMOS_TOPO_NO_MODERATE":
                variables.append('Processing_Flags')
                continue

            if fil.name == "FIL_SMOS_TOPO_NO_STRONG":
                variables.append('Processing_Flags')
                continue

            if fil.name == "FIL_ERA5_TEMP_UNFROZEN":
                era_temp_variable = variable.short_name.replace("wv", "t")
                variables.append(era_temp_variable)
                continue

            if fil.name == "FIL_ERA5_LAND_TEMP_UNFROZEN":
                era_temp_variable = variable.short_name.replace("wv", "t")
                variables.append(era_temp_variable)
                continue

            if fil.name in (
                    "FIL_SMOSL3_STRONG_TOPO_MANDATORY",
                    "FIL_SMOSL3_MODERATE_TOPO",
                    "FIL_SMOSL3_ICE_MANDATORY",
                    "FIL_SMOSL3_FROZEN",
                    "FIL_SMOSL3_URBAN_LOW",
                    "FIL_SMOSL3_URBAN_HIGH",
                    "FIL_SMOSL3_WATER",
                    "FIL_SMOSL3_EXTERNAL",
                    "FIL_SMOSL3_TAU_FO",
            ):
                variables.append('Science_Flags')
                continue

            if fil.name in (
                    "FIL_SMOSL2_OW",
                    "FIL_SMOSL2_SNOW",
                    "FIL_SMOSL2_ICE",
                    "FIL_SMOSL2_FROST",
                    "FIL_SMOSL2_TOPO_S",
            ):
                variables.append('Science_Flags')
                continue

            if fil.name in (
                    "FIL_SMOSL2_RFI_high_confidence",
                    "FIL_SMOSL2_RFI_good_confidence",
            ):
                variables.append('RFI_Prob')
                variables.append('N_RFI_X')
                variables.append('N_RFI_Y')
                variables.append('M_AVA0')
                continue

            if fil.name in (
                    "FIL_SMOSL2_ORBIT_ASC",
                    "FIL_SMOSL2_ORBIT_DES",
                    "FIL_SMAP_L3_V9_ORBIT_ASC",
                    "FIL_SMAP_L3_V9_ORBIT_DSC"
            ):
                variables.append('Overpass')
                continue

            if fil.name == "FIL_CCIGF_GAPMASK":
                variables.append("gapmask")

            if fil.name == "FIL_CCIGF_FROZENMASK":
                variables.append("frozenmask")




    # meaning these are parametrized filters
    except AttributeError:
        for fil in filters:
            if fil.filter.name == "FIL_SMOSL3_RFI":
                variables.append('Ratio_RFI')
                continue

            if fil.filter.name == "FIL_SMOSL2_CHI2P":
                variables.append('Chi_2_P')
                continue
            if fil.filter.name == "FIL_SMAP_L3_V9_VWC":
                variables.append('vegetation_water_content')
                continue

            if fil.filter.name == "FIL_SMAP_L3_V9_static_water_body":
                variables.append('static_water_body_fraction')
                continue

            if fil.filter.name == "FIL_ASCAT_SUBSURFACE_SCAT_PROB":
                variables.append('subsurface_scattering_probability')
                continue

            if fil.filter.name == "FIL_ASCAT_SSM_SENSITIVITY":
                variables.append('surface_soil_moisture_sensitivity')
                continue

    return variables


def setup_filtering(reader, filters, param_filters, dataset,
                    variable) -> tuple:
    # figure out which variables we have to load because we want to use them
    load_vars = get_used_variables(filters, dataset, variable)
    load_vars.extend(get_used_variables(param_filters, dataset, variable))
    __logger.debug(f"Loaded filter variables: {load_vars}")

    # restrict the variables that are read from file in the reader
    if hasattr(reader, 'parameters'):
        __logger.debug("Replacing existing variables to read: {}".format(
            reader.parameters))
        reader.parameters = load_vars

    read_name = 'read'
    read_kwargs = {}

    if not filters and not param_filters:
        __logger.debug('No filters to apply for dataset {}.'.format(dataset))
        return BasicAdapter(reader,
                            read_name=read_name), read_name, read_kwargs

    filtered_reader = reader

    masking_filters = []
    adapter_kwargs = dict()
    # TODO Adapt filters
    for pfil in param_filters:
        __logger.debug(
            f"Setting up parametrised filter {pfil.filter.name} for "
            f"dataset {dataset} with parameter {pfil.parameters}"
        )

        if pfil.filter.name == "FIL_SMOSL3_RFI":
            param = regex_sub(r'[ ]+,[ ]+', ',', pfil.parameters)
            masking_filters.append(('Ratio_RFI', '<=', float(param)))
            continue

        if pfil.filter.name == "FIL_SMOSL2_CHI2P":
            param = regex_sub(r'[ ]+,[ ]+', ',', pfil.parameters)
            masking_filters.append(('Chi_2_P', '>=', float(param)))
            continue

        if pfil.filter.name == "FIL_SMAP_L3_V9_VWC":
            param = regex_sub(r'[ ]+,[ ]+', ',', pfil.parameters)
            masking_filters.append(
                ('vegetation_water_content', '<=', float(param)))
            continue

        if pfil.filter.name == "FIL_SMAP_L3_V9_static_water_body":
            param = regex_sub(r'[ ]+,[ ]+', ',', pfil.parameters)
            masking_filters.append(
                ('static_water_body_fraction', '<=', float(param)))
            continue

        if pfil.filter.name == "FIL_ASCAT_SUBSURFACE_SCAT_PROB":
            param = regex_sub(r'[ ]+,[ ]+', ',', pfil.parameters)
            masking_filters.append(
                ('subsurface_scattering_probability', '<', float(param)))
            continue

        if pfil.filter.name == "FIL_ASCAT_SSM_SENSITIVITY":
            param = regex_sub(r'[ ]+,[ ]+', ',', pfil.parameters)
            masking_filters.append(
                ('surface_soil_moisture_sensitivity', '>', float(param)))
            continue

        inner_reader = filtered_reader
        while hasattr(inner_reader, 'cls'):
            inner_reader = inner_reader.cls

        if pfil.filter.name == "FIL_ISMN_NETWORKS" and pfil.parameters:
            if pfil.parameters == 'ALL':
                networks = [network for network in inner_reader.networks]
                __logger.debug(
                    'Available networks: ' + ';'.join(inner_reader.networks))
                __logger.debug('All networks selected')
                inner_reader.activate_network(networks)
            elif isinstance(inner_reader, ISMN_Interface):
                param = regex_sub(r'[ ]+,[ ]+', ',',
                                  pfil.parameters)  # replace whitespace
                # around commas
                param = regex_sub(r'(^[ ]+|[ ]+$)', '',
                                  param)  # replace whitespace at start and
                # end of string
                paramnetlist = param.split(',')
                networks = [n for n in paramnetlist if
                            n in inner_reader.networks]
                __logger.debug(
                    'Available networks: ' + ';'.join(inner_reader.networks))
                __logger.debug('Selected networks: ' + ';'.join(networks))
                inner_reader.activate_network(networks)
            continue

    for fil in filters:
        __logger.debug(
            "Setting up filter {} for dataset {}.".format(fil.name, dataset))

        if fil.name == "FIL_ALL_VALID_RANGE":
            masking_filters.append(
                (variable.short_name, '>=', variable.min_value))
            masking_filters.append(
                (variable.short_name, '<=', variable.max_value))
            continue

        if fil.name == "FIL_ISMN_GOOD":
            masking_filters.append(('soil_moisture_flag', '==', 'G'))
            continue

        if fil.name == "FIL_C3S_FLAG_0":
            masking_filters.append(('flag', '==', 0))
            continue

        if fil.name == "FIL_C3S_NO_FLAG_1":
            masking_filters.append(('flag', '!=', 1))
            continue

        if fil.name == "FIL_C3S_NO_FLAG_2":
            masking_filters.append(('flag', '!=', 2))
            continue

        if fil.name == "FIL_C3S_MODE_ASC":
            masking_filters.append(('mode', '==', 1))
            continue

        if fil.name == "FIL_C3S_MODE_DESC":
            masking_filters.append(('mode', '==', 2))
            continue

        if fil.name == "FIL_GLDAS_UNFROZEN":
            temp_variable = variable.short_name.replace("Moi", "TMP")
            masking_filters.append(('SWE_inst', '<', 0.001))
            masking_filters.append((variable.short_name, '>', 0.0))
            masking_filters.append((temp_variable, '>', 1.))
            continue

        if fil.name == "FIL_ASCAT_METOP_A":
            masking_filters.append(('sat_id', '==', 3))
            continue

        if fil.name == "FIL_ASCAT_METOP_B":
            masking_filters.append(('sat_id', '==', 4))
            continue

        if fil.name == "FIL_ASCAT_METOP_C":
            masking_filters.append(('sat_id', '==', 5))
            continue

        if fil.name == "FIL_ASCAT_UNFROZEN_UNKNOWN":
            masking_filters.append(
                ('ssf', '<=', 1))  # TODO: really should be == 0 or == 1
            continue

        if fil.name == "FIL_ASCAT_UNFROZEN_UNKNOWN_new":
            masking_filters.append(
                ('surface_flag', '<=', 1))  # TODO: really should be == 0 or == 1
            continue

        if fil.name == "FIL_ASCAT_NO_CONF_FLAGS":
            masking_filters.append(('conf_flag', '==', 0))
            continue

        if fil.name == "FIL_ASCAT_NO_PROC_FLAGS":
            masking_filters.append(('proc_flag', '==', 0))
            continue

        if fil.name == "FIL_ASCAT_NO_PROC_FLAGS_new":
            masking_filters.append(('processing_flag', '==', 0))
            continue

        if fil.name == "FIL_SMOS_QUAL_RECOMMENDED":
            masking_filters.append(('Quality_Flag', '==', 0))
            continue

        if fil.name == "FIL_SMOSL2_RFI_good_confidence":
            def comb_rfi(row):
                # 'COMBINED_RFI' is created using the formula:
                # (N_RFI_X + N_RFI_Y) / M_AVA0 and the class
                # pytesmo.validation_framework.adapters.ColumnCombineAdapter
                return (row['N_RFI_X'] + row['N_RFI_Y']) / row['M_AVA0']

            filtered_reader = ColumnCombineAdapter(filtered_reader,
                                                   comb_rfi,
                                                   func_kwargs={'axis': 1},
                                                   columns=['N_RFI_X',
                                                            'N_RFI_Y',
                                                            'M_AVA0'],
                                                   new_name="COMBINED_RFI")

            masking_filters.append(('COMBINED_RFI', '<=', 0.2))
            masking_filters.append(('RFI_Prob', '<=', 0.2))
            continue

        if fil.name == "FIL_SMOSL2_RFI_high_confidence":
            def comb_rfi(row):
                # 'COMBINED_RFI' is created using the formula:
                # (N_RFI_X + N_RFI_Y) / M_AVA0 and the class
                # pytesmo.validation_framework.adapters.ColumnCombineAdapter
                return (row['N_RFI_X'] + row['N_RFI_Y']) / row['M_AVA0']

            filtered_reader = ColumnCombineAdapter(filtered_reader,
                                                   comb_rfi,
                                                   func_kwargs={'axis': 1},
                                                   columns=['N_RFI_X',
                                                            'N_RFI_Y',
                                                            'M_AVA0'],
                                                   new_name="COMBINED_RFI")

            masking_filters.append(('COMBINED_RFI', '<=', 0.1))
            masking_filters.append(('RFI_Prob', '<=', 0.1))
            continue

        # The BIT-based flagging needs to correspond between the bit index
        # value of the dataset
        # and that given here. In the following, bit index values to be
        # flagged (i.e. the third
        # value passed in the tuples) are 0-based indexed, e.g.:
        # 0b00010 -> [[1]]
        # 0b01010 -> [[1], [3]]
        # =======================================================================================

        if fil.name == "FIL_SMOS_TOPO_NO_MODERATE":
            masking_filters.append(
                ('Processing_Flags', check_normalized_bits_array, [[0]]))
            continue

        if fil.name == "FIL_SMOS_TOPO_NO_STRONG":
            masking_filters.append(
                ('Processing_Flags', check_normalized_bits_array, [[1]]))
            continue

        if fil.name == "FIL_SMOS_UNPOLLUTED":
            masking_filters.append(
                ('Scene_Flags', check_normalized_bits_array, [[2]]))
            continue

        if fil.name == "FIL_SMOS_UNFROZEN":
            masking_filters.append(
                ('Scene_Flags', check_normalized_bits_array, [[3]]))
            continue

        if fil.name == "FIL_SMOS_BRIGHTNESS":
            masking_filters.append(
                ('Processing_Flags', check_normalized_bits_array, [[0]]))
            continue

        if fil.name == "FIL_SMOSL3_STRONG_TOPO_MANDATORY":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[3]]))
            continue

        if fil.name == "FIL_SMOSL3_MODERATE_TOPO":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[4]]))
            continue

        if fil.name == "FIL_SMOSL3_ICE_MANDATORY":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[12]]))
            continue

        if fil.name == "FIL_SMOSL3_FROZEN":
            masking_filters.append(('Science_Flags',
                                    check_normalized_bits_array,
                                    [[6], [7], [8], [11]]))
            continue

        if fil.name == "FIL_SMOSL3_URBAN_LOW":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[15]]))
            continue

        if fil.name == "FIL_SMOSL3_URBAN_HIGH":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[16]]))
            continue

        if fil.name == "FIL_SMOSL3_WATER":
            masking_filters.append(('Science_Flags',
                                    check_normalized_bits_array,
                                    [[5], [13], [14]]))
            continue

        if fil.name == "FIL_SMOSL3_EXTERNAL":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[24], [25]]))
            continue

        if fil.name == "FIL_SMOSL3_TAU_FO":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[27]]))
            continue

        if fil.name == "FIL_SMOSL2_OW":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[5]]))
            continue

        if fil.name == "FIL_SMOSL2_SNOW":
            masking_filters.append(('Science_Flags',
                                    check_normalized_bits_array,
                                    [[7], [8], [6]]))
            continue

        if fil.name == "FIL_SMOSL2_ICE":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[12]]))
            continue

        if fil.name == "FIL_SMOSL2_FROST":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[11]]))
            continue

        if fil.name == "FIL_SMOSL2_TOPO_S":
            masking_filters.append(
                ('Science_Flags', check_normalized_bits_array, [[3]]))
            continue

        if fil.name == "FIL_SMOSL2_ORBIT_DES":
            masking_filters.append(('Overpass', '==', 2))
            continue

        if fil.name == "FIL_SMOSL2_ORBIT_ASC":
            masking_filters.append(('Overpass', '==', 1))
            continue

        # snow depth in the nc file yet, this is the preliminary one.
        if fil.name == "FIL_ERA5_TEMP_UNFROZEN":
            era_temp_variable = variable.short_name.replace("wv", "t")
            masking_filters.append((era_temp_variable, '>', 274.15))
            continue

        if fil.name == "FIL_ERA5_LAND_TEMP_UNFROZEN":
            era_temp_variable = variable.short_name.replace("wv", "t")
            masking_filters.append((era_temp_variable, '>', 274.15))
            continue
        # Select Ascending or descending mode for SMAP L3 Version 9 Data
        if fil.name == "FIL_SMAP_L3_V9_ORBIT_ASC":
            masking_filters.append(('Overpass', '==', 2))
            continue
        if fil.name == "FIL_SMAP_L3_V9_ORBIT_DSC":
            masking_filters.append(('Overpass', '==', 1))
            continue
        # Filters for the CCI GAPFILLED product
        if fil.name == "FIL_CCIGF_GAPMASK":
            masking_filters.append(("gapmask", "==", 0))
        if fil.name == "FIL_CCIGF_FROZENMASK":
            masking_filters.append(("frozenmask", "==", 0))


    if len(masking_filters):
        filtered_reader = AdvancedMaskingAdapter(filtered_reader,
                                                 masking_filters,
                                                 read_name=read_name,
                                                 **adapter_kwargs)
    else:
        filtered_reader = BasicAdapter(filtered_reader, read_name=read_name)

    return filtered_reader, read_name, read_kwargs
