from django.db import models

class Statistics(models.Model):
    class Meta:
        verbose_name_plural = "Statistics"

    id = models.AutoField(primary_key=True)
    collect_statistics = models.BooleanField(default=True)
