import logging
import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import ModelAdmin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import path
from django_countries import countries as base_countries

from validator.models import User, ValidationRun, Dataset, DatasetConfiguration, UptimeReport, UptimeAgent


def sorted_users_validation_query():
    return ValidationRun.objects.values('user').annotate(count=Count('user')).order_by('-count')


def get_time_as_string(time_in_time_format, year_first=True):
    try:
        day = time_in_time_format.day
        month = time_in_time_format.month
        year = time_in_time_format.year
        hour = time_in_time_format.hour
        minute = time_in_time_format.minute if time_in_time_format.minute > 9 else f'0{time_in_time_format.minute}'
    except:
        return 'No date found'

    if year_first:
        time_as_str = f'{year}-{month}-{day} {hour}:{minute}'
    else:
        time_as_str = f'{day}-{month}-{year} {hour}:{minute}'

    return time_as_str


def get_dataset_info_by_user(user=None):
    if user is not None:
        try:
            user_runs = user.validationrun_set.all()
        except:
            return None

        configs = DatasetConfiguration.objects.none()  # just an empty query
        for run in user_runs:
            configs = run.dataset_configurations.all() | configs

    datasets = Dataset.objects.all()
    dataset_names = list(datasets.values_list('short_name', flat=True))
    dataset_counts = []
    dataset_versions = []
    for dataset in datasets:
        versions = dataset.versions.all()
        version_counts = []
        version_names = []
        for version in versions:
            if user is not None:
                number = configs.filter(dataset=dataset, version=version).count()
            else:
                number = dataset.dataset_configurations.filter(version=version).count()
            version_counts.append(number)
            version_names.append(version.short_name)
        dataset_counts.append(version_counts)
        dataset_versions.append(version_names)

    dataset_names.append('User data')
    user_datasets = Dataset.objects.exclude(user=None)
    dataset_versions.append([f'{user_dataset.pretty_name}/{user_dataset.user.username}' for user_dataset in user_datasets])
    dataset_counts.append([user_dataset.dataset_configurations.count() for user_dataset in user_datasets])

    dataset_dict = {'datasets': dataset_names,
                    'versions': dataset_versions,
                    'dataset_count': dataset_counts}
    return dataset_dict


def verify_uptime_percentage(uptime_report):
    if int(uptime_report.uptime_percentage) not in range(50, 101):
        if uptime_report.period == 'DAILY':
            reference_number_of_minutes = 24 * 60
        else:
            month = uptime_report.updated.date().month
            year = uptime_report.updated.date().year
            if month == 2:
                reference_number_of_minutes = 28 * 24 * 60 if (year % 400 == 0) and (year % 100 == 0) else 29 * 24 * 60
            elif month in [1, 3, 5, 7, 8, 10, 12]:
                reference_number_of_minutes = 31 * 24 * 60
            else:
                reference_number_of_minutes = 30 * 24 * 60
        downtime_minutes = uptime_report.downtime_minutes if uptime_report.downtime_minutes >= 0 else 0
        return 100 - downtime_minutes / reference_number_of_minutes
    return uptime_report.uptime_percentage


def verify_downtime_minutes(downtime_minutes):
    if downtime_minutes < 0:
        return 0
    else:
        return downtime_minutes


def check_kpi(uptime_report_item, kpi):
    if kpi == 'downtime_minutes':
        return verify_downtime_minutes(getattr(uptime_report_item, kpi))
    else:
        return verify_uptime_percentage(uptime_report_item)


class StatisticsAdmin(ModelAdmin):
    __logger = logging.getLogger(__name__)

    fields = ['collect_statistics']

    def __init__(self, model, admin_site):
        super(StatisticsAdmin, self).__init__(model, admin_site)

    def get_urls(self):
        urls = super(StatisticsAdmin, self).get_urls()
        new_urls = [
            path('', self.admin_site.admin_view(self.statistics), name='qa4sm-statistics'),
            path('user_id/', self.admin_site.admin_view(ajax_user_info), name='ajax_user_info'),
        ]
        return new_urls + urls

    @staticmethod
    def users_info_for_plot():
        users = User.objects.filter(is_active=True).order_by('pk')
        users_names = [user.username for user in users]
        validations_num = [user.validationrun_set.all().count() for user in users]
        users_dict = {'users': users_names,
                      'validations_num': validations_num}
        return users_dict

    @staticmethod
    def most_frequent_user_info():
        most_frequent_user_id = sorted_users_validation_query().first()['user']
        user_name = User.objects.get(pk=most_frequent_user_id).username
        validations_num = sorted_users_validation_query().first()['count']
        return {'name': user_name, 'validation_num': validations_num}

    @staticmethod
    def validation_info_for_plot():
        validations_sorted_by_time = ValidationRun.objects.order_by('start_time')
        validations_time = list(validations_sorted_by_time.values_list('start_time', flat=True))
        # here the date is converted to the format 'YYYY-MM-DD HH:MM' needed to plotply histogram
        time_list = []
        for time in validations_time:
            time_new_format = get_time_as_string(time)
            time_list.append(time_new_format)

        first = validations_sorted_by_time.values_list('start_time', flat=True).first()
        first_time = [f'{first.year}-{first.month}-{first.day} 0:00:00']
        last = validations_sorted_by_time.values_list('start_time', flat=True).last()
        last_time = [f'{last.year}-{last.month}-{last.day} 23:59:59']

        validation_dict = {'validations': validations_sorted_by_time,
                           'validations_time': time_list,
                           'first_validation': first_time,
                           'last_validation': last_time}

        return validation_dict

    @staticmethod
    def get_kpis_stats():
        uptime_monitoring = UptimeReport.objects.all()
        daily_reports = uptime_monitoring.filter(period="DAILY")
        monthly_reports = uptime_monitoring.filter(period="MONTHLY")
        return monthly_reports

    @staticmethod
    def number_of_users_per_country(distinct_list_of_countries):
        number_of_users_in_country_dict = {}
        for country in distinct_list_of_countries:
            number_of_users_in_country = User.objects.filter(country=country).count()
            country_full_name = base_countries.countries[country]
            number_of_users_in_country_dict[country_full_name] = number_of_users_in_country
        return dict((sorted(number_of_users_in_country_dict.items())))

    @staticmethod
    def get_kpi_info_for_plot(period, kpi):
        uptime_reports = UptimeReport.objects.all().filter(period=period).\
            filter(start_time__gte=datetime.date(2021, 6, 1)).distinct('start_time')
        agents = UptimeAgent.objects.all()

        otput_list = []
        for agent in agents:
            otput_list.append((f'{agent.description}', [[f'{item.created.date()}', check_kpi(item, kpi)] for item in
                                                        uptime_reports.filter(agent_key=agent.agent_key)]))

        return otput_list

    # @csrf_protect_m
    def statistics(self, request):

        if not request.user.is_superuser:
            raise PermissionDenied

        users = User.objects.filter(is_active=True).order_by('pk')
        distinct_list_of_countries = User.objects.filter(is_active=True).exclude(country=''). \
            values_list('country', flat=True).distinct()

        daily_outage = self.get_kpi_info_for_plot("DAILY", 'downtime_minutes')
        daily_uptime = self.get_kpi_info_for_plot("DAILY", 'uptime_percentage')

        monthly_outage = self.get_kpi_info_for_plot("MONTHLY", 'downtime_minutes')
        monthly_uptime = self.get_kpi_info_for_plot("MONTHLY", 'uptime_percentage')

        if request.method == "GET":
            stats = {'users': users,
                     'number_of_users': users.count(),
                     'number_of_staff': users.filter(is_staff=True).count(),
                     'number_of_countries': distinct_list_of_countries.count(),
                     'number_of_validations': ValidationRun.objects.all().count(),
                     'most_frequent_user': self.most_frequent_user_info(),
                     'val_num_by_user_data': self.users_info_for_plot(),
                     'validations_for_plot': self.validation_info_for_plot(),
                     'datasets_for_plot': get_dataset_info_by_user(),
                     'number_of_users_in_country_dict': self.number_of_users_per_country(distinct_list_of_countries),
                     'monthly_outage': monthly_outage,
                     'monthly_uptime': monthly_uptime,
                     'daily_outage': daily_outage,
                     'daily_uptime': daily_uptime}

            return render(request, 'admin/qa4sm_statistics.html', {'stats': stats})


@staff_member_required
def ajax_user_info(request):
    user_id = request.GET.get('user_id')
    try:
        selected_user = User.objects.get(pk=user_id)
    except:
        return HttpResponseBadRequest("No such a user")
    try:
        last_validation = ValidationRun.objects.order_by('start_time').filter(user_id=user_id).last().start_time
        val_num = sorted_users_validation_query().get(user=user_id)['count']
    except:
        last_validation = None
        val_num = 0

    datasets_used = get_dataset_info_by_user(selected_user)
    last_valid_time = get_time_as_string(last_validation, False)
    last_login_time = get_time_as_string(selected_user.last_login, False)

    response_data = {
        'user_name': selected_user.username,
        'val_num': val_num,
        'last_validation': last_valid_time,
        'last_login': last_login_time,
        'datasets_used': datasets_used,
    }

    return JsonResponse(response_data)
