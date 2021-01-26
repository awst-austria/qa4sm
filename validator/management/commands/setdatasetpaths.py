from os import path

from django.core.management.base import BaseCommand

from validator.models import Dataset


class Command(BaseCommand):
    help = "Prompts you for locations of datasets. Can be used to initialise the database."

    def add_arguments(self, parser):
        parser.add_argument('-p', '--path', type=str, help='Path prefix', )

    def handle(self, *args, **options):
        parent_data_folder = options['path']

        if parent_data_folder:
            mode = 'a'
            not_interactive = True
        else:
            mode = input(
                'Do you want to set paths for all datasets (a) or just those that don\'t have one (u)? (default a): ') or 'a'
            mode = 'u' if mode.lower().startswith('u') else 'a'

            parent_data_folder = input(
                '[optional] Set your parent data folder here to auto-generate dataset subfolder suggestions (default: empty): ')

        change_counter = 0
        for dataset in Dataset.objects.all():
            if ((mode == 'u') and bool(dataset.storage_path)):
                continue

            if parent_data_folder:
                default_path = path.join(parent_data_folder, dataset.short_name)
            elif dataset.storage_path:
                default_path = dataset.storage_path
            else:
                default_path = None

            if not not_interactive:
                if default_path:
                    val = input(
                        'Please enter storage location for dataset "{}" (default {}): '.format(dataset.short_name,
                                                                                               default_path)) or default_path
                else:
                    val = input('Please enter storage location for dataset "{}": '.format(dataset.short_name))
            else:
                val = default_path

            print(val)
            dataset.storage_path = val
            dataset.save()
            change_counter += 1

        self.stdout.write(self.style.SUCCESS('Changed datasets: {}'.format(change_counter)))
