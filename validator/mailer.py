import logging

from django.core.mail import send_mail
from django.urls.base import reverse

from valentina.settings import EMAIL_FROM

__logger = logging.getLogger(__name__)

## TODO: put into settings? Get from django?
SITE_URL = "https://qa4sm.eodc.eu"

def send_val_done_notification(val_run):
        __logger.info('Sending mail about validation {} to user {}...'.format(val_run.id, val_run.user))

        url = SITE_URL + reverse('result', kwargs={'result_uuid': val_run.id})

        # enumerate datasets with "and" and Oxford comma.
        dataset_string = ''
        and_position = val_run.dataset_configurations.count() - 1 - (1 if val_run.reference_configuration is not None else 0)
        i = 0
        for dc in val_run.dataset_configurations.all():
            if dc.id != val_run.reference_configuration.id:
                if (i != 0):
                    dataset_string += ", "
                    if (i == and_position):
                        dataset_string += "and "
                dataset_string += "{} ({})".format(dc.dataset.pretty_name, dc.version.pretty_name)
                i += 1

        subject = '[QA4SM] Validation finished'
        body = 'Dear {} {},\n\nyour validation of {} against {} ({}) data has been completed.\nThe results are available at: {}.\n\nBest regards,\nQA4SM team'.format(
            val_run.user.first_name,
            val_run.user.last_name,
            dataset_string,
            val_run.reference_configuration.dataset.pretty_name,
            val_run.reference_configuration.version.pretty_name,
            url)

        _send_email(recipients=[val_run.user.email],
                    subject=subject,
                    body=body)

def send_val_expiry_notification(val_run):
        __logger.info('Sending mail about expiry of validation {} to user {}...'.format(val_run.id, val_run.user))

        url = SITE_URL + reverse('result', kwargs={'result_uuid': val_run.id})

        dataset_name = "{} ({})".format(val_run.name_tag, val_run.id) if val_run.name_tag else str(val_run.id)

        subject = '[QA4SM] Validation expiring soon'
        body = 'Dear {} {},\n\nyour validation {} will expire soon.\nIt will be deleted automatically on {} if you take no further action.\nIf you want to extend the validation\'s lifetime or archive it, please visit {}\n\nBest regards,\nQA4SM team'.format(
            val_run.user.first_name,
            val_run.user.last_name,
            dataset_name,
            val_run.expiry_date,
            url)

        _send_email(recipients=[val_run.user.email],
                    subject=subject,
                    body=body)

def send_new_user_signed_up(user):
        __logger.info('Sending mail about new user {} to admins...'.format(user.username))

        url = SITE_URL + reverse('admin:user_change_status', kwargs={'user_id': user.id})

        subject = '[QA4SM] New user signed up'
        body = 'Dear admins,\n\nnew user {} {} ({}) has signed up.\nTo activate their account go to: {}\n\nBest regards,\nYour webapp'.format(
            user.first_name,
            user.last_name,
            user.username,
            url)

        _send_email(recipients=[EMAIL_FROM],
                    subject=subject,
                    body=body)

def send_user_account_removal_request(user):
        __logger.info('Sending mail about user removal request ({}) to admins...'.format(user.username))

        url = SITE_URL + reverse('admin:validator_user_change', kwargs={'object_id': user.id})
        subject = '[QA4SM] User profile removal request'
        body = 'Dear admins,\n\n A new user account removal request has arrived from {} {} ({}).\nPlease review the account and delete it as soon as possible. \nUser account: {}\n\nBest regards,\nYour webapp'.format(
            user.first_name,
            user.last_name,
            user.username,
            url)

        _send_email(recipients=[EMAIL_FROM],
                    subject=subject,
                    body=body)


def send_user_status_changed(user, activate):
        __logger.info('Sending mail to user {} about {}...'.format(
            user.username,
            ('activation' if activate else 'deactivation')
            ))

        subject = '[QA4SM] Account ' + ('activated' if activate else 'deactivated')
        body = 'Dear {} {},\n\nyour account "{}" has been {}.'.format(
            user.first_name,
            user.last_name,
            user.username,
            ('activated' if activate else 'deactivated'),
            )

        if activate:
            url = SITE_URL + reverse('login')
            body += '\nYou can now log in here: {}'.format(
                url)

        body += '\n\nBest regards,\nQA4SM team'

        _send_email(recipients=[user.email],
                    subject=subject,
                    body=body)

def _send_email(recipients, subject, body):
    try:
        send_mail(subject=subject,
                  message=body,
                  from_email=EMAIL_FROM,
                  recipient_list=recipients,
                  fail_silently=False,)
    except Exception:
        __logger.exception('E-mail could not be sent.')
