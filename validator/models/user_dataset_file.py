from django.db import models
from validator.models.variable import DataVariable
from validator.models.version import DatasetVersion
from validator.models.dataset import Dataset


class UserDatasetFile(models.Model):
    id = models.AutoField(primary_key=True)
    dataset = models.ForeignKey(Dataset, related_name='dataset', on_delete=models.CASCADE)
    version = models.ForeignKey(DatasetVersion, related_name='version', on_delete=models.CASCADE)
    variable =models.ForeignKey(DataVariable, related_name='variable', on_delete=models.CASCADE)