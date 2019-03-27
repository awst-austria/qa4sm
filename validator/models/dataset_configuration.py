import uuid

from django.db import models
from validator.models import DataFilter
from validator.models import Dataset
from validator.models.version import DatasetVersion
from validator.models.variable import DataVariable
from validator.models.validation_run import ValidationRun


class DatasetConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    validation = models.ForeignKey(to=ValidationRun, on_delete=models.PROTECT, related_name='validation', null=False)
    dataset = models.ForeignKey(to=Dataset, on_delete=models.PROTECT, related_name='dataset', null=False)
    version = models.ForeignKey(to=DatasetVersion, on_delete=models.PROTECT, related_name='version', null=False)
    variable = models.ForeignKey(to=DataVariable, on_delete=models.PROTECT, related_name='variable', null=False)
    filters = models.ManyToManyField(DataFilter, related_name='filters')
    reference = models.BooleanField()
    scaling_reference = models.BooleanField()
    
    def __str__(self):
        return "Data set: {}, version: {}, variable: {}, reference: {}, scaling_reference: {}".format(self.dataset.short_name, self.version.short_name,self.variable.short_name,self.reference,self.scaling_reference)
    