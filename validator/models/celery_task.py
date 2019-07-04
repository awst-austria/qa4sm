import uuid

from django.db import models

from validator.models.validation_run import ValidationRun


class CeleryTask(models.Model):
    validation = models.ForeignKey(to=ValidationRun, on_delete=models.CASCADE, related_name='celery_tasks', null=False)
    celery_task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return "task: {}".format(self.celery_task_id)
