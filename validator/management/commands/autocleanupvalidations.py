from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from django.conf import settings
from validator.mailer import send_val_expiry_notification
from validator.models import ValidationRun, CeleryTask, User
import logging


class Command(BaseCommand):
    help = "Removes validations that are past their expiry date. Sends emails to users about validations expiring soon."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        __logger = logging.getLogger(__name__)
        # print("I'm running auto cleanup, so the cronjob works properly")
        __logger.debug(
            "I'm running auto cleanup, so the cronjob works properly"
        )
        users = User.objects.all()
        cleaned_up = []
        notified = []
        for user in users:
            ## no, you can't filter for is_expired because it isn't in the database. but you can exclude running validations
            good_validations = ValidationRun.objects.filter(end_time__isnull=False).filter(user=user)
            canceled_validations = ValidationRun.objects.filter(progress__in=[-1, -100]).filter(user=user)
            validations = good_validations.union(canceled_validations)
            validations_near_expiring = []
            for validation in validations:
                __logger.debug(
                    f'{validation.id} / {user}'
                )
                ## notify user about upcoming expiry if not already done
        #         if ((validation.is_near_expiry) and (not validation.expiry_notified)):
        #             ## if already a quarter of the warning period has passed without a notification being sent (could happen when service is down),
        #             ## extend the validation so that the user gets the full warning period
        #             if timezone.now() + timedelta(days=settings.VALIDATION_EXPIRY_WARNING_DAYS/4) > validation.expiry_date:
        #                 validation.last_extended = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS - settings.VALIDATION_EXPIRY_WARNING_DAYS)
        #                 validation.save()
        #             validations_near_expiring.append(validation)
        #             notified.append(str(validation.id))
        #             continue
        #
        #         ## if validation is expired and user was notified, get rid of it
        #         elif (validation.is_expired and validation.expiry_notified):
        #             vid = str(validation.id)
        #             celery_tasks = CeleryTask.objects.filter(validation_id = validation.id)
        #             for task in celery_tasks:
        #                 task.delete()
        #             validation.delete()
        #             cleaned_up.append(vid)
        #
        #     if len(validations_near_expiring) != 0:
        #         send_val_expiry_notification(validations_near_expiring)
        #
        # # this part refer to validations that belong to a non-existing user -> there is no user to send a notification
        # # to, so we can just remove those validations (apart from published ones)
        # no_user_validations = ValidationRun.objects.filter(user=None)
        # for no_user_val in no_user_validations:
        #     celery_tasks = CeleryTask.objects.filter(validation_id=no_user_val.id)
        #     for task in celery_tasks:
        #         task.delete()
        #     if no_user_val.doi == '':
        #         no_user_val.delete()
        #         cleaned_up.append(str(no_user_val.id))
        #
        # self.stdout.write(self.style.SUCCESS('Notified validations: {}\nAuto-cleaned validations: {}'.format(notified, cleaned_up)))
