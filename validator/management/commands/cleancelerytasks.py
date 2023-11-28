from datetime import datetime

import pytz
from django.core.management import BaseCommand
from validator.models import CeleryTask
from validator.uptime import generate_daily_report, generate_monthly_report


class Command(BaseCommand):
    help = "Clean celery tasks when the worker is restarted"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        celery_tasks = CeleryTask.objects.all()
        celery_tasks.delete()

        self.stdout.write(self.style.SUCCESS('Celery tasks are cleaned'))
