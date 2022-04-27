import logging

from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.core import mail
from django.urls.base import reverse
from django.conf import settings
from api.frontend_urls import get_angular_url

__logger = logging.getLogger(__name__)


def send_val_done_notification(val_run):
        __logger.info('Sending mail about validation {} to user {}...'.format(val_run.id, val_run.user))

        url = settings.SITE_URL + get_angular_url('result', val_run.id)

        # enumerate datasets with "and" and Oxford comma.
        dataset_string = ''
        and_position = val_run.dataset_configurations.count() - 1 - (
            1 if val_run.reference_configuration is not None else 0)
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
        body = 'Dear {} {},\n\nyour validation of {} against {} ({}) data has been completed.\nThe results are available at: {}.\nYou have until {} to inspect your validation - then it will be automatically removed (unless archived).\n\nBest regards,\nQA4SM team'.format(
            val_run.user.first_name,
            val_run.user.last_name,
            dataset_string,
            val_run.reference_configuration.dataset.pretty_name,
            val_run.reference_configuration.version.pretty_name,
            url,
            val_run.expiry_date)

        _send_email(recipients=[val_run.user.email],
                    subject=subject,
                    body=body)


        # url = settings.SITE_URL + '/login/?next=' + get_angular_url('result', val_run.id)
def send_val_expiry_notification(val_runs):
    val_ids = ', '.join([str(val.id) for val in val_runs])
    user = val_runs[0].user
    __logger.info('Sending mail about expiry of validation {} to user {}...'.format(val_ids, user))

    if user is not None:
        urls = []
        val_names = []
        val_dates = []
        for val_run in val_runs:
            urls.append(settings.SITE_URL + '/login/?next=' + get_angular_url('result', val_run.id))
            val_names.append("{} ({})".format(val_run.name_tag, val_run.id) if val_run.name_tag else str(val_run.id))
            val_dates.append(val_run.expiry_date.strftime("%Y-%m-%d %H:%M"))

            val_run.expiry_notified = True
            val_run.save()

        subject = '[QA4SM] Validation expiring soon'

        if len(val_runs) == 1:
            body = 'Dear {} {},\n\nyour validation {} will expire soon.\nIt will be deleted automatically on {} ' \
                  'if you take no further action.\nIf you want to extend the validation\'s lifetime or archive it,' \
                  ' please visit\n{}\n(you will need to log in).\nPlease note that archived and published validations' \
                   ' are not subjected to deletion.\n\nBest regards,\nQA4SM team'.format(
                    user.first_name,
                    user.last_name,
                    val_names[0],
                    val_dates[0],
                    urls[0])
        else:
            body = 'Dear {} {},\n\nyour validations:\n{}\nwill expire soon.\nThey will be deleted automatically on:' \
                   '\n{}\nif you take no further action.\nIf you want to extend the validations\' ' \
                   'lifetime or archive them, ' \
                   'please visit\n{}\n(you will need to log in).\nPlease note that archived and published validations' \
                   ' are not subjected to deletion.\n\nBest regards,\nQA4SM team'.format(
                    user.first_name,
                    user.last_name,
                    ",\n".join(val_names),
                    ",\n".join(val_dates),
                    ",\n".join(urls))

        _send_email(recipients=[user.email],
                    subject=subject,
                    body=body)

        val_run.expiry_notified = True
        val_run.save()

def send_new_user_signed_up(user):
        __logger.info('Sending mail about new user {} to admins...'.format(user.username))

        url = settings.SITE_URL + reverse('admin:user_change_status', kwargs={'user_id': user.id})

        subject = '[QA4SM] New user signed up'
        body = 'Dear admins,\n\nnew user {} {} ({}) has signed up.\nTo activate their account go to: {}\n\nBest regards,\nYour webapp'.format(
            user.first_name,
            user.last_name,
            user.username,
            url)

        _send_email(recipients=[settings.EMAIL_FROM],
                    subject=subject,
                    body=body)


def send_user_account_removal_request(user):
        __logger.info('Sending mail about user removal request ({}) to admins...'.format(user.username))

        url = settings.SITE_URL + reverse('admin:validator_user_change', kwargs={'object_id': user.id})
        subject = '[QA4SM] User profile removal request'
        body = 'Dear admins,\n\n A new user account removal request has arrived from {} {} ({}).\nPlease review the account and delete it as soon as possible. \nUser account: {}\n\nBest regards,\nYour webapp'.format(
            user.first_name,
            user.last_name,
            user.username,
            url)

        _send_email(recipients=[settings.EMAIL_FROM],
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
            url = settings.SITE_URL + get_angular_url('login')
            body += '\nYou can now log in here: {}'.format(
                url)

        body += '\n\nBest regards,\nQA4SM team'

        _send_email(recipients=[user.email],
                    subject=subject,
                    body=body)


def send_user_link_to_reset_password(user, message):
    __logger.info('Sending mail about resetting their password to user {}...'.format(user.username))
    subject = '[QA4SM] Password reset for QA4SM webservice'
    _send_email(recipients=[user.email],
                subject=subject,
                body=message)


def _send_email(recipients, subject, body, html_message=None):
    try:
        connection = mail.get_connection()
        connection.open()
        messages = list()
        for recipient in recipients:
            msg = EmailMultiAlternatives(subject, body, settings.EMAIL_FROM, [recipient])
            if html_message:
                msg.attach_alternative(html_message, "text/html")
            messages.append(msg)
        connection.send_messages(messages)
        connection.close()
    except Exception:
        __logger.exception('E-mail could not be sent.')
