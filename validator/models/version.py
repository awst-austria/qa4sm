from django.db import models
from validator.models.filter import DataFilter
from validator.models.variable import DataVariable


class DatasetVersion(models.Model):
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=40)
    help_text = models.CharField(max_length=150)
    time_range_start = models.TextField(blank=True, null=True)
    time_range_end = models.TextField(blank=True, null=True)
    geographical_range = models.JSONField(blank=True, null=True)
    filters = models.ManyToManyField(DataFilter, related_name='filters', blank=True)
    variables = models.ManyToManyField(DataVariable, related_name='variables')

    def __str__(self):
        return self.short_name
