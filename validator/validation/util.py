import errno
from os import makedirs, listdir, path
import warnings
import inspect


def mkdir_if_not_exists(the_dir):
    try:
        makedirs(the_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def first_file_in(the_dir, extension):
    for file in listdir(the_dir):
        if file.endswith(extension):
            return path.join(the_dir, file)
    return None


def get_function_name() -> str:
    '''Returns the name of the calling function.'''
    frame = inspect.currentframe().f_back
    return frame.f_code.co_name

def determine_status(progress, end_time, current_status):
    """Determine the status based on progress and end_time."""
    if current_status == 'DONE':
        return 'DONE'  # Keep 'DONE' unchanged

    if progress == 0 and not end_time:
        return 'SCHEDULED'
    elif progress == 100 and end_time:
        return 'DONE'
    elif progress < 0:
        return 'CANCELLED'
    elif end_time and progress < 100:
        return 'ERROR'
    else:
        return 'RUNNING'