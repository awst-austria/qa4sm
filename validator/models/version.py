from django.db import models


class DatasetVersion(models.Model):
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=30)
    help_text = models.CharField(max_length=150)
    time_range_start = models.TextField(blank=True, null=True)
    time_range_end = models.TextField(blank=True, null=True)

    # many-to-one relationships coming from other models:
    # dataset_configuration from DatasetConfiguration

    def __str__(self):
        return self.short_name
