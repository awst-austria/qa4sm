from django.shortcuts import get_object_or_404
from qa4sm_preprocessing.utils import preprocess_user_data

from validator.models import UserDatasetFile, DataVariable
from validator.mailer import send_failed_preprocessing_notification


def get_sm_variable_names(variables):
    key_sm_words = ['water', 'soil', 'moisture', 'soil_moisture', 'sm', 'ssm', 'water_content', 'soil', 'moisture',
                    'swi', 'swvl1', 'soilmoi']
    key_error_words = ['error', 'bias', 'uncertainty']
    candidates = [variable for variable in variables if any([word in variable.lower() for word in key_sm_words])
                  and not any([word in variable.lower() for word in key_error_words])]

    sm_variables = [{
        'name': var,
        'long_name': variables[var].get("long_name", var),
        'units': variables[var].get("units") if variables[var].get("units") else 'n.a.'
    } for var in candidates]

    if len(sm_variables) > 0:
        return sm_variables[0]
    else:
        return {'name': '--none--',
                'long_name': '--none--',
                'units': 'n.a.'}


def get_variables_from_the_reader(reader):
    variables = reader.variable_description()
    variables_dict_list = [
        {'name': variable,
         'long_name': variables[variable].get("long_name", variables[variable].get("standard_name", variable)),
         'units': variables[variable].get("units") if variables[variable].get("units") else 'n.a.'
         }
        for variable in variables
    ]

    return variables_dict_list


def user_data_preprocessing(file_uuid, file_path, file_raw_path):
    try:
        gridded_reader = preprocess_user_data(file_path, file_raw_path + '/timeseries')
    except Exception as e:
        file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
        send_failed_preprocessing_notification(file_entry)
        file_entry.delete()
        return

    # I get file entry here and not before preprocessing, as the preprocessing takes time and if a db connection is
    # opened for too long, there is an error thrown. I would have to close the connection and open it one more time
    file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
    sm_variable = get_sm_variable_names(gridded_reader.variable_description())
    all_variables = get_variables_from_the_reader(gridded_reader)

    variable_entry = DataVariable.objects.get(pk=file_entry.variable_id)
    # new_variable_data = {
    #     'help_text': f'Variable {variable_name} of dataset {dataset_name} provided by  user {user}.',
    #     'min_value': max_value,
    #     'max_value': min_value,
    #     'unit': variable_unit if variable_unit else 'n.a.'
    # }
    # update variable
    variable_entry.short_name = sm_variable['name']
    variable_entry.pretty_name = sm_variable['long_name']
    variable_entry.help_text = f'Variable {sm_variable["long_name"]} of dataset ' \
                               f'{file_entry.dataset.pretty_name} provided by user {file_entry.owner.username}.',
    variable_entry.unit = sm_variable['units'] if sm_variable['units'] else 'n.a.'
    try:
        variable_entry.save()
    except Exception as e:
        send_failed_preprocessing_notification(file_entry, True)
        file_entry.delete()

    file_entry.all_variables = all_variables
    file_entry.metadata_submitted = True
    file_entry.save()

    return
