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

        subject = '[QA4SM] Validation finished'
        body = 'Dear {} {},\n\nYour validation of {} ({}) against {} ({}) data has been completed.\nThe results are available at: {}.\n\nBest regards,\nQA4SM team'.format(
            val_run.user.first_name,
            val_run.user.last_name,
            val_run.data_dataset,
            val_run.data_version,
            val_run.ref_dataset,
            val_run.ref_version,
            url)

        _send_email(recipients=[val_run.user.email],
                    subject=subject,
                    body=body)

def send_new_user_signed_up(user):
        __logger.info('Sending mail about new user {} to admins...'.format(user.username))

        # TODO: figure out how to get this url with reverse
        url = SITE_URL + '/admin/validator/user/{}/changestatus/'.format(user.id)

        subject = '[QA4SM] New user signed up'
        body = 'Dear admins,\n\nnew user {} {} ({}) has signed up.\nTo activate their account go to: {}\n\nBest regards,\nYour webapp'.format(
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
