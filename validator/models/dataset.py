from django.db import models
# from validator.models.filter import DataFilter
from validator.models.variable import DataVariable
from validator.models.version import DatasetVersion
from django.conf import settings


class Dataset(models.Model):
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=30)
    help_text = models.CharField(max_length=150)

    storage_path = models.CharField(max_length=255, blank=True)

    detailed_description = models.TextField()
    source_reference = models.TextField()
    citation = models.TextField()

    is_spatial_reference = models.BooleanField(default=False)
    is_scattered_data = models.BooleanField(default=False)

    versions = models.ManyToManyField(DatasetVersion, related_name='versions')


    # filters = models.ManyToManyField(DataFilter, related_name='filters') #TODO this must be put into version.py
    resolution = models.JSONField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    user_groups = models.ManyToManyField(to='DataManagementGroup', related_name='custom_datasets', null=True,
                                         blank=True)

    # many-to-one relationships coming from other models:
    # dataset_configuration from DatasetConfiguration

    def __str__(self):
        return self.short_name

    @property
    def is_shared(self):
        return len(self.user_groups.all())

    @property
    def not_as_reference(self):
        # I know it should be imported globally, but it doesn't work then
        from validator.validation.globals import NOT_AS_REFERENCE
        return self.short_name in NOT_AS_REFERENCE

    @property
    def resolution_in_m(self):
        # we need the resolution in m in the distance lookup
        # as a default value we use 30km
        default = 30e3
        if not isinstance(self.resolution, dict):
            return default
        if not "value" in self.resolution or not "unit" in self.resolution:
            return default
        val = self.resolution["value"]
        unit = self.resolution["unit"]
        if unit == "km":
            return val * 1e3
        elif unit == "deg":
            # assuming 1deg approx 100km
            return val * 100 * 1e3
        else:
            return default
