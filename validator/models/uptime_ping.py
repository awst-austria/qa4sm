from django.db import models


class UptimePing(models.Model):
    id = models.AutoField(primary_key=True)
    agent_key = models.CharField(max_length=200)
    time = models.DateTimeField()
