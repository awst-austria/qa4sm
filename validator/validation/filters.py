import logging

import pandas as pd
from django.core.exceptions import ValidationError
from pytesmo.validation_framework.adapters import AdvancedMaskingAdapter
from ismn.interface import ISMN_Interface
from re import sub as regex_sub
import numpy as np
from validator.models import DataFilter

__logger = logging.getLogger(__name__)

'''
Bitmask filter for SMOS, you can only exclude data on set bits (not on unset bits)
'''
def smos_exclude_bitmask(data, bitmask):
    thedata = data

    if type(thedata) is pd.Series:
        thedata = thedata.values

    mask = (thedata & bitmask) != bitmask
    return mask

'''
Get the variables that need to be loaded for filtering the data on them.
'''
def get_used_variables(filters, dataset, variable):

    variables = [ variable.pretty_name ]

    if not filters:
        return variables

    for fil in filters:
        if(fil.name == "FIL_ISMN_GOOD"):
            variables.append('soil moisture_flag')
            continue

        if((fil.name == "FIL_C3S_FLAG_0") or
           (fil.name == "FIL_C3S_NO_FLAG_1") or
           (fil.name == "FIL_C3S_NO_FLAG_2")):
            variables.append('flag')
            continue

        if((fil.name == "FIL_C3S_MODE_ASC") or
           (fil.name == "FIL_C3S_MODE_DESC")):
            variables.append('mode')
            continue

        if(fil.name == "FIL_GLDAS_UNFROZEN"):
            temp_variable = variable.pretty_name.replace("Moi", "TMP")
            variables.append(temp_variable)
            variables.append('SWE_inst')
            continue

        if((fil.name == "FIL_ASCAT_METOP_A") or
           (fil.name == "FIL_ASCAT_METOP_B")):
            variables.append('sat_id')
            continue

        if(fil.name == "FIL_ASCAT_UNFROZEN_UNKNOWN"):
            variables.append('ssf')
            continue

        if(fil.name == "FIL_ASCAT_NO_CONF_FLAGS"):
            variables.append('conf_flag')
            continue

        if(fil.name == "FIL_ASCAT_NO_PROC_FLAGS"):
            variables.append('proc_flag')
            continue

        if(fil.name == "FIL_SMOS_QUAL_RECOMMENDED"):
            variables.append('Quality_Flag')
            continue

        if(fil.name == "FIL_SMOS_UNFROZEN"):
            variables.append('Scene_Flags')
            variables.append('Soil_Temperature_Level1')
            continue

        if(fil.name == "FIL_SMOS_UNPOLLUTED"):
            variables.append('Scene_Flags')
            continue

        if(fil.name == "FIL_SMOS_BRIGHTNESS"):
            variables.append('Processing_Flags')
            continue

        if(fil.name == "FIL_SMOS_TOPO_NO_MODERATE"):
            variables.append('Processing_Flags')
            continue

        if(fil.name == "FIL_SMOS_TOPO_NO_STRONG"):
            variables.append('Processing_Flags')
            continue

        if(fil.name == "FIL_ERA5_TEMP_UNFROZEN"):
            era_temp_variable = variable.pretty_name.replace("wv", "t")
            variables.append(era_temp_variable)
            continue

        if(fil.name == "FIL_ERA5_LAND_TEMP_UNFROZEN"):
            era_temp_variable = variable.pretty_name.replace("wv", "t")
            variables.append(era_temp_variable)
            continue

    return variables


def setup_filtering(reader, filters, param_filters, dataset, variable):

    # figure out which variables we have to load because we want to use them
    load_vars = get_used_variables(filters, dataset, variable)

    # restrict the variables that are read from file in the reader
    if hasattr(reader.cls, 'parameters'):
        __logger.debug("Replacing existing variables to read: {}".format(reader.cls.parameters))
        reader.cls.parameters = load_vars

    if not filters and not param_filters:
        __logger.debug('No filters to apply for dataset {}.'.format(dataset))
        return reader

    filtered_reader = reader

    for pfil in param_filters:
        __logger.debug("Setting up parametrised filter {} for dataset {} with parameter {}".format(pfil.filter.name, dataset, pfil.parameters))

        inner_reader = filtered_reader
        while (hasattr(inner_reader, 'cls')):
            inner_reader = inner_reader.cls

        if(pfil.filter.name == "FIL_ISMN_NETWORKS" and pfil.parameters):

            if isinstance(inner_reader, ISMN_Interface):
                param = regex_sub(r'[ ]+,[ ]+', ',', pfil.parameters) # replace whitespace around commas
                param = regex_sub(r'(^[ ]+|[ ]+$)', '', param) # replace whitespace at start and end of string
                paramnetlist = param.split(',')
                networks = [ n for n in paramnetlist if n in inner_reader.list_networks() ]
                __logger.debug('Available networks: ' + ';'.join(inner_reader.list_networks()))
                __logger.debug('Selected networks: ' + ';'.join(networks))
                inner_reader.activate_network(networks)
            continue

        if isinstance(inner_reader, ISMN_Interface):
            default_depth = DataFilter.objects.get(name='FIL_ISMN_DEPTH').default_parameter
            default_depth = [float(depth) for depth in default_depth.split(',')]
            depth_min = default_depth[0]
            depth_max = default_depth[1]

            if pfil.filter.name == "FIL_ISMN_DEPTH" and pfil.parameters:
                depth_min = float(pfil.parameters.split(',')[0])
                depth_max = float(pfil.parameters.split(',')[1])
                if depth_min < 0 or depth_max < 0:
                    raise ValidationError({'filter': 'Depth range can not be negative'})
                if depth_min > depth_max:
                    raise  ValidationError({'filter': 'The minimal depth can not be higher than the maximal one'})

            indices = [ind for ind, data in enumerate(inner_reader.metadata) if data[3] < depth_min or data[3] > depth_max]
            inner_reader.metadata = np.delete(inner_reader.metadata, indices)


    masking_filters = []

    for fil in filters:
        __logger.debug("Setting up filter {} for dataset {}.".format(fil.name, dataset))

        if(fil.name == "FIL_ALL_VALID_RANGE"):
            masking_filters.append( (variable.pretty_name, '>=', variable.min_value) )
            masking_filters.append( (variable.pretty_name, '<=', variable.max_value) )
            continue

        if(fil.name == "FIL_ISMN_GOOD"):
            masking_filters.append( ('soil moisture_flag', '==', 'G') )
            continue

        if(fil.name == "FIL_C3S_FLAG_0"):
            masking_filters.append( ('flag', '==', 0) )
            continue

        if(fil.name == "FIL_C3S_NO_FLAG_1"):
            masking_filters.append( ('flag', '!=', 1) )
            continue

        if(fil.name == "FIL_C3S_NO_FLAG_2"):
            masking_filters.append( ('flag', '!=', 2) )
            continue

        if(fil.name == "FIL_C3S_MODE_ASC"):
            masking_filters.append( ('mode', '==', 1) )
            continue

        if(fil.name == "FIL_C3S_MODE_DESC"):
            masking_filters.append( ('mode', '==', 2) )
            continue

        if(fil.name == "FIL_GLDAS_UNFROZEN"):
            temp_variable = variable.pretty_name.replace("Moi", "TMP")
            masking_filters.append( ('SWE_inst', '<', 0.001) )
            masking_filters.append( (variable.pretty_name, '>', 0.0) )
            masking_filters.append( (temp_variable, '>', 1.) )
            continue

        if(fil.name == "FIL_ASCAT_METOP_A"):
            masking_filters.append( ('sat_id', '==', 3) )
            continue

        if(fil.name == "FIL_ASCAT_METOP_B"):
            masking_filters.append( ('sat_id', '==', 4) )
            continue

        if(fil.name == "FIL_ASCAT_UNFROZEN_UNKNOWN"):
            masking_filters.append( ('ssf', '<=', 1) ) ## TODO: really should be == 0 or == 1
            continue

        if(fil.name == "FIL_ASCAT_NO_CONF_FLAGS"):
            masking_filters.append( ('conf_flag', '==', 0) )
            continue

        if(fil.name == "FIL_ASCAT_NO_PROC_FLAGS"):
            masking_filters.append( ('proc_flag', '==', 0) )
            continue

        if(fil.name == "FIL_SMOS_QUAL_RECOMMENDED"):
            masking_filters.append( ('Quality_Flag', '==', 0) )
            continue

        if(fil.name == "FIL_SMOS_TOPO_NO_MODERATE"):
            masking_filters.append( ('Processing_Flags', smos_exclude_bitmask, 0b00000001) )
            continue

        if(fil.name == "FIL_SMOS_TOPO_NO_STRONG"):
            masking_filters.append( ('Processing_Flags', smos_exclude_bitmask, 0b00000010) )
            continue

        if(fil.name == "FIL_SMOS_UNPOLLUTED"):
            masking_filters.append( ('Scene_Flags', smos_exclude_bitmask, 0b00000100) )
            continue

        if(fil.name == "FIL_SMOS_UNFROZEN"):
            masking_filters.append( ('Scene_Flags', smos_exclude_bitmask, 0b00001000) )
            continue

        if(fil.name == "FIL_SMOS_BRIGHTNESS"):
            masking_filters.append( ('Processing_Flags', smos_exclude_bitmask, 0b00000001) )
            continue

        #snow depth in the nc file yet, this is the preliminary one.
        if(fil.name == "FIL_ERA5_TEMP_UNFROZEN"):
            era_temp_variable = variable.pretty_name.replace("wv", "t")
            masking_filters.append( (era_temp_variable, '>', 274.15) )
            continue

        if(fil.name == "FIL_ERA5_LAND_TEMP_UNFROZEN"):
            era_temp_variable = variable.pretty_name.replace("wv", "t")
            masking_filters.append( (era_temp_variable, '>', 274.15) )
            continue

    if len(masking_filters):
        filtered_reader = AdvancedMaskingAdapter(filtered_reader, masking_filters)

    return filtered_reader
