from django.db import models

class DataFilter(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=80)
    help_text = models.CharField(max_length=150)

    def __str__(self):
        return "{} ({})".format(self.name, self.description)
