from django.db import models

class DataVariable(models.Model):
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, default='n.a.')
    help_text = models.CharField(max_length=150)

    min_value = models.FloatField(null=True)
    max_value = models.FloatField(null=True)
    display_name = models.CharField(max_length=100, default='n.a.', blank=True)

    
    # many-to-one relationships coming from other models:
    # dataset_configuration from DatasetConfiguration

    def __str__(self):
        return self.short_name
