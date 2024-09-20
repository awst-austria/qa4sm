from validator.models import Dataset
from os import path

def set_dataset_paths():
    for dataset in Dataset.objects.all():
        dataset.storage_path = path.join('testdata/input_data', dataset.short_name)
        dataset.save()
