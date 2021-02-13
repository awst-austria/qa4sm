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

    if len(masking_filters):
        filtered_reader = AdvancedMaskingAdapter(filtered_reader, masking_filters)

    return filtered_reader
