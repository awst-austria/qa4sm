from os import path
from ismn.interface import ISMN_Interface
from validator.hacks import TimezoneAdapter
from validator.validation import globals
from validator.validation.input_readers.cgls_csar_ssm_readers import CSarSsmTiffReader
from smos.smos_ic.interface import SMOSTs

def create_reader(dataset, version):
    reader = None

    folder_name = path.join(dataset.storage_path, version.short_name)

    if dataset.short_name == globals.ISMN:
        reader = ISMN_Interface(folder_name)

    if dataset.short_name == globals.CGLS_CSAR_SSM1km:
        cgls_1km_ssm_folder = path.join(folder_name, 'tiff')
        reader = CSarSsmTiffReader(cgls_1km_ssm_folder, grid_sampling=500)
        # todo:setup or not?

    if dataset.short_name == globals.SMOS:
        reader = SMOSTs(folder_name, ioclass_kws={'read_bulk':True})

    if not reader:
        raise ValueError("Reader for dataset '{}' not available".format(dataset))

    reader = TimezoneAdapter(reader)

    return reader
