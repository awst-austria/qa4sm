import logging

from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import render
from django.urls import path

from valentina.celery import app
from validator.models import User, ValidationRun
from django.contrib import messages


class StatisticsAdmin(ModelAdmin):
    __logger = logging.getLogger(__name__)

    fields = ['collect_statistics']

    def __init__(self, model, admin_site):
        super(StatisticsAdmin, self).__init__(model, admin_site)

    def get_urls(self):
        urls = super(StatisticsAdmin, self).get_urls()
        new_urls = [
            path('', self.admin_site.admin_view(self.statistics), name='qa4sm-statistics'),
        ]
        return new_urls + urls

    @staticmethod
    def active_users_number():
        users = User.objects.filter(is_active=True)
        return users.count()

    @staticmethod
    def number_of_run_validations():
        validations = ValidationRun.objects.all()
        return validations.count()

    @staticmethod
    def sorted_users_validation_query():
        return ValidationRun.objects.values('user').annotate(count=Count('user')).order_by('-count')
    
    @staticmethod
    def users_dict():
        users = User.objects.filter(is_active=True)
        users_names = [user.username for user in users]
        validations_num = [user.validationrun_set.all().count() for user in users]
        users_dict = {'users': users_names,
                      'validations_num': validations_num}
        return users_dict

    def most_frequent_user_info(self):
        most_frequent_user_id = self.sorted_users_validation_query().first()['user']
        user_name = User.objects.get(pk=most_frequent_user_id).username
        validations_num = self.sorted_users_validation_query().first()['count']
        return {'name': user_name, 'validation_num': validations_num}

    # @csrf_protect_m
    def statistics(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied

        if request.method == "GET":
            users = User.objects.filter(is_active=True)
            sorted_users = self.sorted_users_validation_query()
            stats = {'users': users,
                     'number_of_users': self.active_users_number(),
                     'number_of_validations': self.number_of_run_validations(),
                     'most_frequent_user': self.most_frequent_user_info(),
                     'sorted_users': sorted_users,
                     'val_num_by_user_data': self.users_dict()}

            return render(request, 'admin/qa4sm_statistics.html', {'stats': stats})
