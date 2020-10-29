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
    def sorted_users_validation_query():
        return ValidationRun.objects.values('user').annotate(count=Count('user')).order_by('-count')
    
    @staticmethod
    def users_info_for_plot():
        users = User.objects.filter(is_active=True).order_by('pk')
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

    @staticmethod
    def validation_info_for_plot():
        validations_sorted_by_time = ValidationRun.objects.order_by('start_time')
        validations_time = list(validations_sorted_by_time.values_list('start_time', flat=True))
        # here the date is converted to the format 'YYYY-MM-DD HH:MM' needed to plotply histogram
        time_list = []
        for time in validations_time:
            # if the minute part is a single digit then 0 has to be added, otherwise it's not converted correctly
            minute = time.minute if time.minute > 9 else f'0{time.minute}'
            time_new_format = f'{time.year}-{time.month}-{time.day} {time.hour}:{minute}'
            time_list.append(time_new_format)

        first = validations_sorted_by_time.values_list('start_time', flat=True).first()
        first_time = [f'{first.year}-{first.month}-{first.day} 0:00:00']
        last = validations_sorted_by_time.values_list('start_time', flat=True).last()
        last_time = [f'{last.year}-{last.month}-{last.day}']

        validation_dict = {'validations': validations_sorted_by_time,
                           'validations_time': time_list,
                           'first_validation': first_time,
                           'last_validation': last_time}
        return validation_dict

    # @csrf_protect_m
    def statistics(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied

        if request.method == "GET":
            stats = {'number_of_users':  User.objects.filter(is_active=True).count(),
                     'number_of_validations':  ValidationRun.objects.all().count(),
                     'most_frequent_user': self.most_frequent_user_info(),
                     'val_num_by_user_data': self.users_info_for_plot(),
                     'validations_for_plot': self.validation_info_for_plot()}

            return render(request, 'admin/qa4sm_statistics.html', {'stats': stats})
