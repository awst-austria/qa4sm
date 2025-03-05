import logging
from datetime import timedelta

from django.utils import timezone
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.core import mail
from django.urls.base import reverse
from django.conf import settings
from api.frontend_urls import get_angular_url
from valentina.settings_conf import EMAIL_HOST_USER

# from validator.models import UserDatasetFile

__logger = logging.getLogger(__name__)


def send_failed_preprocessing_notification(file_entry, too_long_variable_name=False):
    __logger.info(f'Sending mail about failed preprocessing of the {file_entry.id} to user {file_entry.owner}...')
    guidelines_url = settings.SITE_URL + get_angular_url('my-datasets')

    file_problem_body = (f"Your file containing data for dataset {file_entry.dataset.pretty_name}, version "
                         f"{file_entry.version.pretty_name} could not be processed. Please check if you "
                         f"uploaded proper file and if your file hs been prepared according to our"
                         f" guidelines ({guidelines_url}).\n")

    variable_problem_body = (f"Looks like the variable name used in the file is too long. Please note that the "
                             f"variable name can not be longer than 30 characters and the long_name can not be "
                             f"longer than 100 characters.\n")

    subject = '[QA4SM] File preprocessing failed'
    body = f"""Dear {file_entry.owner.first_name} {file_entry.owner.last_name}, \n\n
    {file_problem_body if not too_long_variable_name else variable_problem_body}
    In case of further problems, please contact our team.\n\nBest regards,\nQA4SM team'"""

    _send_email(recipients=[file_entry.owner.email],
                subject=subject,
                body=body)


def send_val_done_notification(val_run):
    __logger.info('Sending mail about validation {} to user {}...'.format(val_run.id, val_run.user))

    url = settings.SITE_URL + get_angular_url('result', val_run.id)

    # enumerate datasets with "and" and Oxford comma.
    dataset_string = ''
    and_position = val_run.dataset_configurations.count() - 1 - (
        1 if val_run.spatial_reference_configuration is not None else 0)
    i = 0
    for dc in val_run.dataset_configurations.all():
        if dc.id != val_run.spatial_reference_configuration.id:
            if (i != 0):
                dataset_string += ", "
                if (i == and_position):
                    dataset_string += "and "
            dataset_string += "{} ({})".format(dc.dataset.pretty_name, dc.version.pretty_name)
            i += 1

    subject = '[QA4SM] Validation finished'
    body = 'Dear {} {},\n\nyour validation of {} with  {} ({})  data ' \
           'as spatial reference and  {} ({}) data  as temporal reference has been ' \
           'completed.\nThe results are available at: {}.\nYou have until {} to inspect your validation - ' \
           'then it will be automatically removed (unless archived).\n\nBest regards,\nQA4SM team'.format(
        val_run.user.first_name,
        val_run.user.last_name,
        dataset_string,
        val_run.spatial_reference_configuration.dataset.pretty_name,
        val_run.spatial_reference_configuration.version.pretty_name,
        val_run.temporal_reference_configuration.dataset.pretty_name,
        val_run.temporal_reference_configuration.version.pretty_name,
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
        for val_run in val_runs:
            val_run.expiry_notified = True
            val_run.save()

        subject = '[QA4SM] Validation expiring soon'
        greetings_form = f'{user.first_name}  {user.last_name}' if user.first_name and user.last_name else user.username
        threshold_date = timezone.now() - timedelta(days=settings.VALIDATION_EXPIRY_DAYS)
        removal_date = timezone.now() + timedelta(days=settings.VALIDATION_EXPIRY_WARNING_DAYS)
        help_url = settings.SITE_URL + get_angular_url('help')
        my_results_url = settings.SITE_URL + get_angular_url('validations')

        body = f'''Dear {greetings_form},
        \nyour validations started before {threshold_date.date()} will expire soon. \nThey will be deleted automatically on {removal_date.date()} if you take no further action. \nIf you want to extend the validation\'s lifetime or archive it, please visit {my_results_url}(you will need to log in).
        \nPlease note that archived and published validations are not subjected to deletion. If you need assistance with archiving or publishing your results, please visit our help ({help_url}) page for detailed guidance and support.
        \nBest regards,
        \nQA4SM team
        '''

        if user.email:
            _send_email(recipients=[user.email],
                        subject=subject,
                        body=body)
        else:
            __logger.exception('The user has no email assigned')


def send_new_user_signed_up(user):
    __logger.info('Sending mail about new user {} to admins...'.format(user.username))

    url = settings.SITE_URL + reverse('admin:user_change_status', kwargs={'user_id': user.id})

    subject = '[QA4SM] New user signed up'
    body = 'Dear admins,\n\nnew user {} {} ({}) has signed up and a verification email has been sent to their provided address\n Kind regards,\nYour webapp'.format(
        user.first_name,
        user.last_name,
        user.username,
        url)

    _send_email(recipients=[settings.EMAIL_FROM],
                subject=subject,
                body=body)

def send_new_user_verification(user, token):
    __logger.info('Sending email verification to user {}...'.format(user.id))

    help_url = settings.SITE_URL + get_angular_url('help')
    #verification_url = settings.SITE_URL + get_angular_url('verify', token)
    verification_url = f"{settings.SITE_URL}/api/verify-email/{user.id}/{token}/"

    subject = '[QA4SM] Verify your email address'
    body = f'''Dear {user.first_name or user.username},
    thank you for signing up to QA4SM. To complete your registration, please verify your email address by clicking the following link: 
    
    {verification_url}

    This link will expire in 24 hours. If you have any problems please contact the admins at {help_url}.

    Kind regards,
    QA4SM team
    '''
    print(user.email)
    print(subject)
    print(body)

    try:
        _send_email(recipients=[user.email],
                    subject=subject,
                    body=body)
    except Exception as e:
        __logger.error(f'Failed to send verification email to user {user.id}: {str(e)}')
        raise

def send_autocleanup_failed(message):
    __logger.info('Sending mail about failing cleanup')
    subject = '[QA4SM INTERNAL] Cleanup failed'
    body = f'Dear admins,\nRunning auto cleanup failed. The error is {message} \nBest regards,\nYour webapp'
    print(body)
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


def send_user_help_request(user_name, user_email, message, send_copy_to_user):
    __logger.info(f'Sending user request from  {user_name}')
    subject = "[USER MESSAGE] - Sent via contact form"
    final_message = f'''Sent by: {user_name} \nReply to: {user_email} \n\n{message}'''
    print(final_message)
    _send_email(recipients=[EMAIL_HOST_USER, user_email] if send_copy_to_user else [EMAIL_HOST_USER],
                subject=subject,
                body=final_message)


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
        print('email sent')
        connection.close()
    except Exception:
        __logger.exception('E-mail could not be sent.')
