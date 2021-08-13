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

    list_display = ('date', 'content')

    def __init__(self, model, admin_site):
        super(EmailAdmin, self).__init__(model, admin_site)

    # def get_urls(self):
    #     urls = super(SendEmailToUsers, self).get_urls()
    #     new_urls = [
    #         path('', self.admin_site.admin_view(self.send_email), name='send-email')
    #     ]
    #
    #     return new_urls + urls
    #
    # def send_email(self, request):
    #     # here I'll create a send email form
    #     context = self.admin_site.each_context(request)
    #     return render(request, 'admin/send_email.html', context)