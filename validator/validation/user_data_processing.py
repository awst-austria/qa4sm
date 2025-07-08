from django.shortcuts import get_object_or_404
from qa4sm_preprocessing.utils import preprocess_user_data

from validator.models import UserDatasetFile, DataVariable
from validator.mailer import send_failed_preprocessing_notification
import logging
from pathlib import Path


def _setup_file_logger(file_uuid, user_path):
    """Setup a file logger for the preprocessing task."""
    logger = logging.getLogger(f"{__name__}.{file_uuid}")
    if not logger.handlers:  # Avoid duplicate handlers
        handler = logging.FileHandler(Path(user_path) / f"{file_uuid}.log")
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def get_sm_variable_names(variables):
    key_sm_words = [
        'water', 'soil', 'moisture', 'soil_moisture', 'sm', 'ssm',
        'water_content', 'soil', 'moisture', 'swi', 'swvl1', 'soilmoi'
    ]
    key_error_words = ['error', 'bias', 'uncertainty']
    candidates = [
        variable for variable in variables
        if any([word in variable.lower() for word in key_sm_words])
        and not any([word in variable.lower() for word in key_error_words])
    ]

    sm_variables = [{
        'name':
        var,
        'long_name':
        variables[var].get("long_name", var),
        'units':
        variables[var].get("units") if variables[var].get("units") else 'n.a.'
    } for var in candidates]

    if len(sm_variables) > 0:
        return sm_variables[0]
    else:
        return {'name': '--none--', 'long_name': '--none--', 'units': 'n.a.'}


def get_variables_from_the_reader(reader):
    variables = reader.variable_description()
    variables_dict_list = [{
        'name':
        variable,
        'long_name':
        variables[variable].get(
            "long_name", variables[variable].get("standard_name", variable)),
        'units':
        variables[variable].get("units")
        if variables[variable].get("units") else 'n.a.'
    } for variable in variables]

    return variables_dict_list


def user_data_preprocessing(file_uuid, file_path, file_raw_path, user_path):
    file_logger = _setup_file_logger(file_uuid, user_path)
    try:
        file_logger.info(f"Starting preprocessing for file {file_uuid}")
        gridded_reader = preprocess_user_data(file_path,
                                              file_raw_path + '/timeseries')
    except Exception as e:
        import traceback
        full_traceback = traceback.format_exc()
        file_logger.error(f"Preprocessing failed: {full_traceback}")
        file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
        send_failed_preprocessing_notification(file_entry)
        file_entry.delete()
        return

    file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
    sm_variable = get_sm_variable_names(gridded_reader.variable_description())
    all_variables = get_variables_from_the_reader(gridded_reader)

    variable_entry = DataVariable.objects.get(pk=file_entry.variable_id)
    variable_entry.short_name = sm_variable['name']
    variable_entry.pretty_name = sm_variable['long_name']
    variable_entry.help_text = f'Variable {sm_variable["long_name"]} of dataset ' \
                               f'{file_entry.dataset.pretty_name} provided by user {file_entry.owner.username}.',
    variable_entry.unit = sm_variable['units'] if sm_variable[
        'units'] else 'n.a.'

    try:
        variable_entry.save()
        file_logger.info("Variable entry saved successfully")
    except Exception as e:
        import traceback
        full_traceback = traceback.format_exc()
        file_logger.error(f"Variable save failed: {full_traceback}")
        send_failed_preprocessing_notification(file_entry,
                                               too_long_variable_name=True)
        file_entry.delete()
        return

    file_entry.all_variables = all_variables
    file_entry.metadata_submitted = True
    file_entry.save()

    file_logger.info(
        f"Preprocessing completed successfully for file {file_uuid}")
    return
