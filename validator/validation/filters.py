import logging

from pytesmo.validation_framework.adapters import SelfMaskingAdapter

__logger = logging.getLogger(__name__)

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
            variables.append('Quality_flag')
            continue

    return variables


def setup_filtering(reader, filters, dataset, variable):

    # figure out which variables we have to load because we want to use them
    load_vars = get_used_variables(filters, dataset, variable)

    # restrict the variables that are read from file in the reader
    if hasattr(reader.reader, 'parameters'):
        __logger.debug("Replacing existing variables to read: {}".format(reader.reader.parameters))
        reader.reader.parameters = load_vars

    if not filters:
        __logger.debug('No filters to apply for dataset {}.'.format(dataset))
        return reader

    filtered_reader = reader

    for fil in filters:
        __logger.debug("Setting up filter {} for dataset {}.".format(fil.name, dataset))

        if(fil.name == "FIL_ALL_VALID_RANGE"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '>=', variable.min_value, variable.pretty_name)
            filtered_reader = SelfMaskingAdapter(filtered_reader, '<=', variable.max_value, variable.pretty_name)
            continue

        if(fil.name == "FIL_ISMN_GOOD"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '==', 'G', 'soil moisture_flag')
            continue

        if(fil.name == "FIL_C3S_FLAG_0"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '==', 0, 'flag')
            continue

        if(fil.name == "FIL_C3S_NO_FLAG_1"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '!=', 1, 'flag')
            continue

        if(fil.name == "FIL_C3S_NO_FLAG_2"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '!=', 2, 'flag')
            continue

        if(fil.name == "FIL_C3S_MODE_ASC"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '==', 1, 'mode')
            continue

        if(fil.name == "FIL_C3S_MODE_DESC"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '==', 2, 'mode')
            continue

        if(fil.name == "FIL_GLDAS_UNFROZEN"):
            temp_variable = variable.pretty_name.replace("Moi", "TMP")
            filtered_reader = SelfMaskingAdapter(filtered_reader, '<', 0.001, 'SWE_inst')
            filtered_reader = SelfMaskingAdapter(filtered_reader, '>', 0.0, variable.pretty_name)
            filtered_reader = SelfMaskingAdapter(filtered_reader, '>', 1., temp_variable)
            continue

        if(fil.name == "FIL_ASCAT_METOP_A"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '==', 3, 'sat_id')
            continue

        if(fil.name == "FIL_ASCAT_METOP_B"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '==', 4, 'sat_id')
            continue

        if(fil.name == "FIL_ASCAT_UNFROZEN_UNKNOWN"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '<=', 1, 'ssf') ## TODO: really should be == 0 or == 1
            continue

        if(fil.name == "FIL_ASCAT_NO_CONF_FLAGS"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '==', 0, 'conf_flag')
            continue

        if(fil.name == "FIL_ASCAT_NO_PROC_FLAGS"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '==', 0, 'proc_flag')
            continue

        if(fil.name == "FIL_SMOS_QUAL_RECOMMENDED"):
            filtered_reader = SelfMaskingAdapter(filtered_reader, '==', 0, 'Quality_flag')
            continue

    return filtered_reader
