from django.db import models

from validator.models import DatasetVersion


class ISMNNetworks(models.Model):
    name = models.CharField(max_length=60)
    continent = models.CharField(max_length=24)
    country = models.CharField(max_length=60)
    number_of_stations = models.IntegerField()
    versions = models.ManyToManyField(DatasetVersion, related_name='network_version')
    station_info = models.CharField(max_length=200000, default='{}')

    def __str__(self):
        return self.name
