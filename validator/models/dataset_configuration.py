import uuid

from django.db import models
from validator.models import DataFilter
from validator.models import Dataset
from validator.models.version import DatasetVersion
from validator.models.variable import DataVariable


class DatasetConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_dataset = models.ForeignKey(to=Dataset, on_delete=models.PROTECT, related_name='data_dataset', null=True)
    data_version = models.ForeignKey(to=DatasetVersion, on_delete=models.PROTECT, related_name='data_version', null=True)
    data_variable = models.ForeignKey(to=DataVariable, on_delete=models.PROTECT, related_name='data_variable', null=True)
    data_filters = models.ManyToManyField(DataFilter, related_name='data_filters')
    reference = models.BooleanField()
    scaling_reference = models.BooleanField()