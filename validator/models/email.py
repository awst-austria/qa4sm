from django.db import models
from validator.models import User
from django.utils import timezone

class Email(models.Model):
    send_to = models.ManyToManyField(User, related_name='addressees')
    content = models.TextField()
    date = models.DateTimeField(null=True, default=timezone.now)
    sent = models.BooleanField(default=False)