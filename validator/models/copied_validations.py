from django.db import models
from validator.models import User


class CopiedValidations(models.Model):
    id = models.AutoField(primary_key=True)
    copied_run = models.ForeignKey('ValidationRun', on_delete=models.CASCADE, related_name='copied_run', null=True)
    used_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    original_run = models.ForeignKey('ValidationRun', on_delete=models.SET_NULL, null=True, related_name='original_run')
    original_run_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "copied run: {}, user: {}, original run: {} )".format(self.copied_run, self.used_by_user, self.original_run)

