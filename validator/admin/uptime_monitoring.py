import logging
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

            context = {
                'daily_statistics': daily_statistics,
                'monthly_statistics': monthly_statistics
            }
            print(context)
            return TemplateResponse(request, 'admin/uptime_report.html', context)
