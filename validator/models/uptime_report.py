from django.db import models


class UptimeReport(models.Model):
    DAILY = 'DAILY'
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    YEARLY = 'YEARLY'

    PERIOD_CHOICES = (
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    )

    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    period = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        null=False,
        blank=False,
    )
    uptime_percentage = models.FloatField(null=False, blank=False)
    agent_key = models.CharField(max_length=200, default='unknown')
