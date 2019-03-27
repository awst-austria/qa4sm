import uuid

from django.db import models

from validator.models.validation_run import ValidationRun


class CeleryTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    validation = models.ForeignKey(to=ValidationRun, on_delete=models.PROTECT, related_name='validation', null=False)
    celery_task = models.UUIDField(null=False)

    def __str__(self):
        return "task: {}".format(self.celery_task)
