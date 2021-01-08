from django.db import models
from validator.models import User
from validator.models.validation_run import ValidationRun

class ValidationRun_User(models.Model):

    copied_run = models.ForeignKey(ValidationRun, on_delete=models.CASCADE, related_name='copied_run')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_run = models.ForeignKey(ValidationRun, on_delete=models.SET_NULL, null=True, related_name='original_run')