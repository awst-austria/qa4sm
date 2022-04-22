import logging
import datetime
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.shortcuts import redirect
from django.urls.base import reverse

from validator.models import UptimeAgent, UptimeReport
import statistics
from django.urls import path
from django.template.response import TemplateResponse


def get_service_uptime_statistics(queryset, daily=True, monthly=False):
    if daily:
        reports = queryset.filter(period='DAILY')
    elif monthly:
        reports = queryset.filter(period='MONTHLY')
    else:
        reports = queryset

    if len(reports) != 0:
        downtime_minutes = reports.values_list('downtime_minutes', flat=True)
        uptime_percentage = reports.values_list('uptime_percentage', flat=True)

        max_downtime_minutes = max(downtime_minutes)
        min_uptime_percentage = min(uptime_percentage)
        number_of_maximum_downtime = len(reports.filter(downtime_minutes=max_downtime_minutes))
        dates_of_maximum_downtime = reports.filter(downtime_minutes=max_downtime_minutes) \
            .values_list('start_time', flat=True)

        average_downtime_minutes = statistics.mean(downtime_minutes)
        median_downtime_minutes = statistics.median(downtime_minutes)
        return {
            'max_downtime_minutes': max_downtime_minutes,
            'min_uptime_percentage': min_uptime_percentage,
            'number_of_maximum_downtime': number_of_maximum_downtime,
            'dates_of_maximum_downtime': dates_of_maximum_downtime,
            'average_downtime_minutes': average_downtime_minutes,
            'median_downtime_minutes': median_downtime_minutes
        }

    else:
        return


def get_kpi_info_for_plot(queryset, period, kpi):
    uptime_reports = queryset.filter(period=period).filter(start_time__gte=datetime.date(2021, 6, 1)).distinct('start_time')
    agents = UptimeAgent.objects.all()

    otput_list = []
    for agent in agents:
        otput_list.append((f'{agent.description}', [[f'{item.created.date()}', check_kpi(item, kpi)] for item in
                                                    uptime_reports.filter(agent_key=agent.agent_key)]))

    return otput_list


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


def bulk_get_uptime_statistics(modeladmin, request, queryset):
    try:
        report_ids = queryset.values_list('id', flat=True)
        report_ids_string = ''
        for report_id in report_ids:
            report_ids_string += f'{report_id},'

        return redirect(reverse('admin:get_uptime_statistics', args=[report_ids_string]))
    except Exception as e:
        modeladmin.message_user(message='Error activating user: {}'.format(e))


bulk_get_uptime_statistics.short_description = "Get statistics on the service uptime"


# some additional filtering
class AgentNameFilter(SimpleListFilter):
    title = 'agent name'
    parameter_name = 'agent_name'

    def lookups(self, request, model_admin):
        agents = UptimeAgent.objects.all()
        list_of_lookups = [(agent.description, agent.description) for agent in agents]
        return list_of_lookups

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(agent_key=UptimeAgent.objects.get(description=self.value()).agent_key)


class UptimeMonitoringAdmin(ModelAdmin):
    __logger = logging.getLogger(__name__)
    actions = []

    list_display = (
        'id', 'created', 'updated', 'start_time', 'end_time', 'period', 'uptime_percentage', 'downtime_minutes',
        'agent_name')
    list_filter = ('period', 'created', AgentNameFilter,)
    ordering = ('period', 'created', 'downtime_minutes', 'uptime_percentage')

    def __init__(self, model, admin_site):
        super(UptimeMonitoringAdmin, self).__init__(model, admin_site)
        self.actions += [bulk_get_uptime_statistics]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [path('uptime_statistics/<str:ids>/', self.admin_site.admin_view(self.get_uptime_statistics),
                            name='get_uptime_statistics')]
        return custom_urls + urls

    def agent_name(self, obj):
        return UptimeAgent.objects.get(agent_key=obj.agent_key).description

    def get_uptime_statistics(self, request, ids):
        if request.method == "GET":
            ids_list_string = ids.rstrip(',').split(',')
            ids_list = [int(id_string) for id_string in ids_list_string]
            queryset = UptimeReport.objects.filter(id__in=ids_list)
            daily_statistics = get_service_uptime_statistics(queryset)
            monthly_statistics = get_service_uptime_statistics(queryset, False, True)

            daily_outage = get_kpi_info_for_plot(queryset.filter(period="DAILY"), "DAILY", 'downtime_minutes')
            daily_uptime = get_kpi_info_for_plot(queryset.filter(period="DAILY"), "DAILY", 'uptime_percentage')

            monthly_outage = get_kpi_info_for_plot(queryset.filter(period="MONTHLY"), "MONTHLY", 'downtime_minutes')
            monthly_uptime = get_kpi_info_for_plot(queryset.filter(period="MONTHLY"), "MONTHLY", 'uptime_percentage')

            context = {
                'daily_statistics': daily_statistics,
                'monthly_statistics': monthly_statistics,
                'daily_outage': daily_outage,
                'daily_uptime': daily_uptime,
                'monthly_outage': monthly_outage,
                'monthly_uptime': monthly_uptime
            }
            print(context)
            return TemplateResponse(request, 'admin/uptime_report.html', context)
