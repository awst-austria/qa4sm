import errno
from os import makedirs, listdir, path
import warnings
import inspect
import zipfile


def mkdir_if_not_exists(the_dir):
    try:
        makedirs(the_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def first_file_in(the_dir, extension, val_type="temporal"):
    substringlist = ["Spatial", "SPATIAL", "spatial"]
    for file in listdir(the_dir):
        if val_type=="temporal":
            if (file.endswith(extension)) and not (any(ss in file for ss in substringlist)):
                return path.join(the_dir, file)
        elif val_type=="spatial":
            if (file.endswith(extension)) and (any(ss in file for ss in substringlist)):
                return path.join(the_dir, file)
    return None


def get_function_name() -> str:
    '''Returns the name of the calling function.'''
    frame = inspect.currentframe().f_back
    return frame.f_code.co_name

def determine_status(progress, end_time, progress_spatial=None, val_type=None, 
                     output_file=None, output_file_spatial=None):
    
    """Determine the status based on progress, end_time and output files."""
    
    if val_type == 'spatial':
        relevant_progress = progress_spatial if progress_spatial is not None else progress
    elif val_type == 'both':
        relevant_progress = min(progress, progress_spatial) if progress_spatial is not None else progress
    else:
        relevant_progress = progress

    if relevant_progress == 0 and not end_time:
        if val_type == 'both' and progress_spatial is not None and progress_spatial > 0:
            return 'RUNNING'
        if val_type == 'both' and progress is not None and progress > 0:
            return 'RUNNING'
        return 'SCHEDULED'
    elif relevant_progress < 0:
        return 'CANCELLED'
    elif end_time and relevant_progress == 100:
        if val_type == 'spatial' and not output_file_spatial:
            return 'ERROR'
        elif val_type == 'temporal' and not output_file:
            return 'ERROR'
        elif val_type == 'both':
            if not output_file and not output_file_spatial:
                return 'ERROR'
            if not output_file or not output_file_spatial:
                return 'RUNNING'  # one file missing — still in progress
        return 'DONE'
    elif end_time and relevant_progress < 100 and val_type != 'both':
        return 'ERROR'
    else:
        return 'RUNNING'

def has_csv_in_zip(file):
    """
    Quick check if ZIP contains at least one CSV file
    """
    try:
        # Save current position
        original_pos = file.tell()
        file.seek(0)

        with zipfile.ZipFile(file, 'r') as zip_ref:
            # Just get the file list - no extraction needed
            file_list = zip_ref.namelist()
            has_csv = any(f.lower().endswith('.csv') for f in file_list)
            return has_csv

    except (zipfile.BadZipFile, Exception):
        return False
    finally:
        # Always restore file position
        file.seek(original_pos)