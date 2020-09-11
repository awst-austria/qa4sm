from django.core.management.base import BaseCommand

from validator.models import Dataset


class Command(BaseCommand):
    help = "Lists paths for each dataset from the data base. Paths are set with 'setdatasetpaths'"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for dataset in Dataset.objects.all():
            print(dataset.storage_path)
