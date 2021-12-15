from django.dispatch import receiver
from django.template.loader import render_to_string

from django_rest_passwordreset.signals import reset_password_token_created
from django_rest_passwordreset.models import get_password_reset_token_expiry_time
from api.frontend_urls import get_angular_url
from validator.mailer import _send_email


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url':
            instance.request.build_absolute_uri(get_angular_url('set-password', reset_password_token.key)),
        'password_reset_timeout_hours': get_password_reset_token_expiry_time()
    }
    # render email text
    email_message = render_to_string('email/user_reset_password.html', context)

    subject = '[QA4SM] Password reset for QA4SM webservice'
    _send_email(recipients=[reset_password_token.user.email],
                subject=subject,
                body=email_message)