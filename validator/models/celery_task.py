from django.db import models

from validator.models.validation_run import ValidationRun


class CeleryTask(models.Model):
    validation = models.ForeignKey(to=ValidationRun, on_delete=models.PROTECT, related_name='validation', null=False)
    celery_task = models.UUIDField(null=False)

    def __str__(self):
        return "task: {}".format(self.celery_task)
