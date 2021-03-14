from os import path
from ismn.interface import ISMN_Interface
from validator.hacks import TimezoneAdapter
from validator.validation import globals
from validator.validation.input_readers.cgls_s1_readers import CglsS1TiffReader
from smos.smos_ic.interface import SMOSTs

def create_reader(dataset, version):
    reader = None

    folder_name = path.join(dataset.storage_path, version.short_name)

    if dataset.short_name == globals.ISMN:
        reader = ISMN_Interface(folder_name)

    if dataset.short_name == globals.CGLS_CSAR_SSM1km:
        cgls_1km_ssm_folder = path.join(folder_name, 'tiff')
        reader = CglsS1TiffReader(cgls_1km_ssm_folder, grid_sampling=500, param='CGLS_SSM')

    if dataset.short_name == globals.CGLS_SCATSAR_SWI1km:
        cgls_1km_swi_folder = path.join(folder_name, 'tiff')
        reader = CglsS1TiffReader(cgls_1km_swi_folder, grid_sampling=500, param='CGLS_SWI')

    if dataset.short_name == globals.SMOS:
        reader = SMOSTs(folder_name, ioclass_kws={'read_bulk':True})

    if not reader:
        raise ValueError("Reader for dataset '{}' not available".format(dataset))

    reader = TimezoneAdapter(reader)

    return reader
