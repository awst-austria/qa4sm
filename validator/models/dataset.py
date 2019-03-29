from django.db import models
from validator.models import DataFilter
from validator.models import DataVariable
from validator.models import DatasetVersion


class Dataset(models.Model):
    short_name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=30)
    help_text = models.CharField(max_length=150)

    source_reference = models.TextField()
    citation = models.TextField()

    is_reference = models.BooleanField(default=False)

    versions = models.ManyToManyField(DatasetVersion, related_name='versions')
    variables = models.ManyToManyField(DataVariable, related_name='variables')

    filters = models.ManyToManyField(DataFilter, related_name='filters')
    
    # many-to-one relationships coming from other models:
    # dataset_configuration from DatasetConfiguration

    def __str__(self):
        return self.short_name
