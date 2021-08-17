from django.db import models


class Continent(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
