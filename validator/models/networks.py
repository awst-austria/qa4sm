from django.db import models

from validator.models import DatasetVersion


class ISMNNetworks(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=60)
    continent = models.CharField(max_length=24)
    country = models.CharField(max_length=60)
    versions = models.ManyToManyField(DatasetVersion, related_name='network_version')

    def __str__(self):
        return self.name
