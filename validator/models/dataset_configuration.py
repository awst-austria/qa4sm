from django.db import models

from validator.models import DataFilter
from validator.models import Dataset
from validator.models.variable import DataVariable
from validator.models.version import DatasetVersion


class DatasetConfiguration(models.Model):
    # validator.models.validation_run.ValidationRun
    validation = models.ForeignKey(to='ValidationRun', on_delete=models.CASCADE, related_name='dataset_configurations', null=False)
    dataset = models.ForeignKey(to=Dataset, on_delete=models.PROTECT, related_name='dataset_configurations', null=False)
    version = models.ForeignKey(to=DatasetVersion, on_delete=models.PROTECT, related_name='dataset_configurations', null=False)
    variable = models.ForeignKey(to=DataVariable, on_delete=models.PROTECT, related_name='dataset_configurations', null=False)
    filters = models.ManyToManyField(DataFilter, related_name='dataset_configurations')
#     reference = models.BooleanField()

    def __str__(self):
        return "Data set: {}, version: {}, variable: {}".format(
            self.dataset if hasattr(self, 'dataset') else "none",
            self.version if hasattr(self, 'version') else "none",
            self.variable if hasattr(self, 'variable') else "none",
            )
