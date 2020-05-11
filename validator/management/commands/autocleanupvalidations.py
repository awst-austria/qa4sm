from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from valentina.settings import VALIDATION_EXPIRY_DAYS, VALIDATION_EXPIRY_WARNING_DAYS
from validator.mailer import send_val_expiry_notification
from validator.models import ValidationRun


class Command(BaseCommand):
    help = "Removes validations that are past their expiry date. Sends emails to users about validations expiring soon."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        validations = ValidationRun.objects.filter(end_time__isnull=False) ## no, you can't filter for is_expired because it isn't in the database. but you can exclude running validations
        cleaned_up = []
        notified = []
        for validation in validations:
            ## notify user about upcoming expiry if not already done
            if ((validation.is_near_expiry) and (not validation.expiry_notified)):

                ## if already a quarter of the warning period has passed without a notification being sent (could happen when service is down),
                ## extend the validation so that the user gets the full warning period
                if timezone.now() + timedelta(days=VALIDATION_EXPIRY_WARNING_DAYS/4) > validation.expiry_date:
                    validation.last_extended = timezone.now() - timedelta(days=VALIDATION_EXPIRY_DAYS - VALIDATION_EXPIRY_WARNING_DAYS)
                    validation.save()

                send_val_expiry_notification(validation)
                notified.append(str(validation.id))
                continue

            ## if validation is expired and user was notified, get rid of it
            elif (validation.is_expired and validation.expiry_notified):
                validation.delete()
                cleaned_up.append(str(validation.id))

        self.stdout.write(self.style.SUCCESS('Notified validations: {}\nAuto-cleaned validations: {}'.format(notified, cleaned_up)))
