import errno
from os import makedirs, listdir, path
import warnings


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
