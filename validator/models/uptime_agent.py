from django.db import models


class UptimeAgent(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    agent_key = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    active = models.BooleanField(default=False)
