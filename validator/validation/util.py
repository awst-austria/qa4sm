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
    for file in listdir(the_dir):
        if val_type=="temporal":
            if (file.endswith(extension)) and ("SPATIAL" not in file) and ("spatial" not in file):
                return path.join(the_dir, file)
        elif val_type=="spatial":
            if (file.endswith(extension)) and ("SPATIAL" in file):
                return path.join(the_dir, file)
    return None


def get_function_name() -> str:
    '''Returns the name of the calling function.'''
    frame = inspect.currentframe().f_back
    return frame.f_code.co_name

def determine_status(progress, end_time, current_status, progress_spatial=None, val_type=None):
    """Determine the status based on progress and end_time."""
    if current_status == 'DONE':
        return 'DONE'  # Keep 'DONE' unchanged
    
    if val_type == 'spatial':
        relevant_progress = progress_spatial
    elif val_type == 'both':
        # both temporal and spatial progress must be considered, take the minimum of the two if spatial progress is available
        relevant_progress = min(progress, progress_spatial) if progress_spatial is not None else progress
    else:
        relevant_progress = progress

    if relevant_progress == 0 and not end_time:
        return 'SCHEDULED'
    elif relevant_progress == 100 and end_time:
        return 'DONE'
    elif relevant_progress < 0:
        return 'CANCELLED'
    elif end_time and relevant_progress < 100:
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