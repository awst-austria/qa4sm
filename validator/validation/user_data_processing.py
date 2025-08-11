from django.shortcuts import get_object_or_404
from qa4sm_preprocessing.utils import preprocess_user_data, validate_file_upload

from validator.models import UserDatasetFile, DataVariable
from validator.mailer import send_failed_preprocessing_notification
import logging
from pathlib import Path


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

def run_upload_format_check(file, filename, file_uuid, user_path):
    """Validate uploaded file format and handle results."""
    file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
    # Update file entry with validation results
    file_entry.log_info = f"Starting format validation for file {file_uuid}"

    try:
        success, msg, status = validate_file_upload(file, filename)
         
        if not success:
            file_entry.log_info += f"\n{msg}"
        
        file_entry.log_info += f"\nFormat validation {'succeeded' if success else 'failed'}"
        file_entry.status = 'success' if success else 'failed'
        file_entry.error_message = f"{msg}"
        file_entry.metadata_submitted = True
        file_entry.save()

        return success, msg, status

    except Exception as e:
        file_entry.log_info += f"\nExeption in Format Validation: {str(e)}"
        file_entry.status = 'failed'
        file_entry.error_message = f"Unexpected error during format validation"
        file_entry.metadata_submitted = True
        file_entry.save()

        #  Same return format for run_upload_format_check
        return False, "Unexpected error during validation", 500

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
    file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
    file_entry.log_info +=f"\nStarting preprocessing for file {file_uuid}"
    
    try:
        gridded_reader = preprocess_user_data(file_path,
                                              file_raw_path + '/timeseries')
    except Exception as e:
        import traceback
        full_traceback = traceback.format_exc()
        file_entry.log_info += f"\nPreprocessing failed: {full_traceback}"
        file_entry.status = 'failed'
        file_entry.error_message = f"Unexpected error during preprocessing"
        file_entry.metadata_submitted = True
        file_entry.save()
        
        return

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
        file_entry.log_info +=f"\nVariable entry saved successfully"
    
    except Exception as e:
        import traceback
        full_traceback = traceback.format_exc()
        file_entry.log_info += f"\nVariable save failed: {full_traceback}"
        file_entry.status = 'failed'
        file_entry.error_message = f"Variable save failed"
        file_entry.metadata_submitted = True
        file_entry.save()

        return

    file_entry.all_variables = all_variables
    file_entry.log_info +=f"\nPreprocessing completed successfully"
    file_entry.status = 'success'
    file_entry.error_message = f"Success"
    file_entry.metadata_submitted = True
    file_entry.save()

    file_logger.info(
        f"Preprocessing completed successfully for file {file_uuid}")
    return
