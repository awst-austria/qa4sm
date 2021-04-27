from datetime import datetime

import pytz
from django.core.management import BaseCommand

from validator.uptime import generate_daily_report, generate_monthly_report


class Command(BaseCommand):
    help = "Processes uptime pings and generates daily and monthly reports for the current date"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        date = datetime.now(tz=pytz.UTC)
        generate_daily_report(date)
        generate_monthly_report(year=date.year, month=date.month)

        self.stdout.write(self.style.SUCCESS('Reports have been generated'))
