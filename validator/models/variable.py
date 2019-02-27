from django.db import models

class DataVariable(models.Model):
    short_name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=30)
    help_text = models.CharField(max_length=150)

    min_value = models.FloatField(null=True)
    max_value = models.FloatField(null=True)

    def __str__(self):
        return self.short_name
