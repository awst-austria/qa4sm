import logging

from django.urls import path

from validator.models import Email
from django.contrib.admin import ModelAdmin
from django.shortcuts import render

def bulk_send_email_to_users(modeladmin, request, quesryset):
    for user in quesryset:
        print(user)
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
    # def get_urls(self):
    #     urls = super(EmailAdmin, self).get_urls()
    #     new_urls = [
    #         path('send-email', self.admin_site.admin_view(self.send_email), name='send-email')
    #     ]
    #
    #     return new_urls + urls

    # def send_email(self, request):
    #     # here I'll create a send email form
    #     context = self.admin_site.each_context(request)
    #     return render(request, 'admin/send_email.html')