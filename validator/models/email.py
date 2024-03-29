from django.db import models
from validator.models import User
from django.utils import timezone
from validator.mailer import _send_email
from django.conf import settings
from django.template.loader import get_template
from django.utils.html import strip_tags


class Email(models.Model):
    id = models.AutoField(primary_key=True)
    send_to = models.ManyToManyField(User, related_name='addressees')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    date = models.DateTimeField(null=True, default=timezone.now)
    send_this_email = models.BooleanField(default=False, verbose_name='Send this email')
    sent = models.BooleanField(default=False)

    def send_email(self):
        message_template = get_template('admin/email.html')
        html_message_content = message_template.render({'message': self.content})
        plain_message = strip_tags(html_message_content)

        recipients = [user.email for user in self.send_to.all() if user.email != '']
        if len(recipients) != 0:
            _send_email(recipients, self.subject, plain_message, html_message=html_message_content)
        else:
            body = f'The email entitled {self.subject} can not be sent, as there were no recipients chosen.'
            _send_email([settings.EMAIL_FROM], 'Empty Addressees List', body)
