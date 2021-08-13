import logging

from django.shortcuts import redirect

from validator.models import Email
from django.contrib.admin import ModelAdmin

def bulk_send_email_to_users(modeladmin, request, queryset):
    recipients = [user.email for user in queryset if user.email is not '']
    new_email = Email(subject='', content='')
    new_email.save()
    for user in queryset:
        new_email.send_to.add(user.id)
        new_email.save()
    print(recipients)
    redirect_to = f'/admin/validator/email/{new_email.pk}/change'
    return redirect(redirect_to)

bulk_send_email_to_users.short_description = 'Send an email to the chosen users'


class EmailAdmin(ModelAdmin):
    __logger = logging.getLogger(__name__)
    model = Email
    fields = ('send_to', 'subject','content', 'date', 'send_this_email' )
    list_display = ('date', 'subject','content')

    def __init__(self, model, admin_site):
        super(EmailAdmin, self).__init__(model, admin_site)

    def save_related(self, request, form, formsets, change):
        super(EmailAdmin, self).save_related(request, form, formsets, change)
        if form.instance.send_this_email and not form.instance.sent:
            form.instance.send_email()
            form.instance.sent = True
            form.instance.save()