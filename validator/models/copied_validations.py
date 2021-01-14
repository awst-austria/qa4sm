from django.db import models
from validator.models import User
from validator.models.validation_run import ValidationRun


class CopiedValidations(models.Model):

    copied_run = models.ForeignKey(ValidationRun, on_delete=models.CASCADE, related_name='copied_run', null=True)
    used_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    original_run = models.ForeignKey(ValidationRun, on_delete=models.SET_NULL, null=True, related_name='original_run')

    def __str__(self):
        return "copied run: {}, user: {}, original run: {} )".format(self.copied_run, self.user, self.original_run)