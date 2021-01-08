from django.db import models
from validator.models import User
from validator.models.validation_run import ValidationRun

class ValidationRun_User(models.Model):

    validationrun = models.ForeignKey(ValidationRun, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    original_start = models.DateTimeField('started')
    original_end = models.DateTimeField('finished')