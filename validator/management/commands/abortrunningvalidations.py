from django.core.management.base import BaseCommand
from datetime import datetime
from dateutil.tz import tzlocal
from validator.models import ValidationRun

class Command(BaseCommand):
    help = "Sets interrupted validations' statuses to error. WARNING! Do not run this command while the service is running"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        aborted_validations=ValidationRun.objects.filter(progress__range=(0, 99))
        for val in aborted_validations:
            val.progress=-100
            val.end_time=datetime.now(tzlocal())
            val.save()

        self.stdout.write(self.style.SUCCESS('Aborted validations: %s' % len(aborted_validations)))
