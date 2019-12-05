from django.db import models

class DataFilter(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=80)
    help_text = models.CharField(max_length=150)
    parameterised = models.BooleanField(default=False)
    dialog_name = models.CharField(max_length=30, null=True)
    default_parameter = models.TextField(null=True)

    # many-to-one relationships coming from other models:
    # dataset_configuration from DatasetConfiguration

    def __str__(self):
        return "{} ({})".format(self.name, self.description)
