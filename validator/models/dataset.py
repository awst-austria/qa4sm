from django.db import models
from validator.models.filter import DataFilter
from validator.models.variable import DataVariable
from validator.models.version import DatasetVersion



class Dataset(models.Model):
    short_name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=30)
    help_text = models.CharField(max_length=150)

    storage_path = models.CharField(max_length=255, blank=True)

    detailed_description = models.TextField()
    source_reference = models.TextField()
    citation = models.TextField()

    is_only_reference = models.BooleanField(default=False)

    versions = models.ManyToManyField(DatasetVersion, related_name='versions')
    variables = models.ManyToManyField(DataVariable, related_name='variables')

    filters = models.ManyToManyField(DataFilter, related_name='filters')
    resolution = models.JSONField(null=True)
    
    # many-to-one relationships coming from other models:
    # dataset_configuration from DatasetConfiguration

    def __str__(self):
        return self.short_name

    @property
    def not_as_reference(self):
        # I know it should be imported globally, but it doesn't work then
        from validator.validation.globals import NOT_AS_REFERENCE
        return self.short_name in NOT_AS_REFERENCE
