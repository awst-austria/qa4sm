from django.core.management.base import BaseCommand
import os

from validator.models import DatasetVersion, Dataset
from ismn.interface import ISMN_Interface
from validator.validation.readers import create_reader


class Command(BaseCommand):
    help = "Create the list of ISMN sensor locations that the user can " \
           "download from the `My datasets` page. This will also collect " \
           "ISMN metadata and create the `python_metedata` directory if it " \
           "doesn't exist yet."

    def add_arguments(self, parser):
        parser.add_argument("target_path", type=str,
                            help='Directory where the ISMN sensor location '
                                 'list will be stored in (existing file will '
                                 'be overwritten).', )
        parser.add_argument('-s', '--short_name', type=str,
                            help='Optional. Short Name of the ISMN version '
                                 'to base the list on. If not specified, '
                                 'we use the latest version (based on the ID '
                                 'in the fixtures).', )

    def _get_path_latest_ismn_version(self):
        for dataset in Dataset.objects.all():
            if dataset.short_name == "ISMN":
                latest_version = [v for v in dataset.versions.all()][-1]
                return dataset, latest_version

    def handle(self, *args, **options):
        dataset, version = self._get_path_latest_ismn_version()

        target_path = options['target_path']

        print(f"Create user ISMN station list: \n "
              f"From data: {dataset.storage_path}/{version.short_name} \n "
              f"Target directory: {target_path}")

        ds: ISMN_Interface = create_reader(dataset, version)

        columns = [
            ('network', 'val'),
            ('station', 'val'),
            ('instrument', 'val'),
            ('latitude', 'val'),
            ('longitude', 'val'),
            ('instrument', 'depth_from'),
            ('instrument', 'depth_to'),
            ('timerange_from', 'val'),
            ('timerange_to', 'val'),
        ]

        new_names = ['Network name', 'Station name', 'Instrument',
                     'Latitude [deg]', 'Longitude [deg]',
                     'Depth from [cm]', 'Depth to [cm]',
                     'Period from', 'Period to']

        if 'frm_class' in ds.metadata.columns.get_level_values(0):
            columns.append(('frm_class', 'val'))
            new_names.append('FRM Class')

        df = ds.metadata.loc[:, columns]
        df.columns = df.columns.droplevel(1)
        df.columns = new_names
        df.index.name = 'index'

        fname = os.path.join(target_path, "ismn_station_list.csv")

        df.to_csv(fname, index=False)
