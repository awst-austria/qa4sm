from django.db import models


class DataFilter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=80)
    help_text = models.CharField(max_length=150)
    parameterised = models.BooleanField(default=False)
    dialog_name = models.CharField(max_length=30, null=True, blank=True)
    default_parameter = models.TextField(null=True, blank=True)
    to_include = models.CharField(max_length=150, null=True, blank=True)
    disable_filter = models.IntegerField(null=True)
    threshold = models.BooleanField(default=False),
    default_threshold = models.FloatField(null=True),
    min_threshold = models.FloatField(null=True),
    max_threshold = models.FloatField(null=True),

    # many-to-one relationships coming from other models:
    # dataset_configuration from DatasetConfiguration

    def __str__(self):
        return "{} ({})".format(self.name, self.description)
