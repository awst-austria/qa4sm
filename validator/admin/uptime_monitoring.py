import logging
from django.contrib.admin import ModelAdmin


class UptimeMonitoringAdmin(ModelAdmin):
    __logger = logging.getLogger(__name__)

    list_display = ('id', 'created', 'updated', 'start_time', 'end_time', 'period', 'uptime_percentage', 'downtime_minutes', 'agent_key')
    list_filter = ('period', 'created')
    ordering = ('period', 'created', 'downtime_minutes', 'uptime_percentage')

    def __init__(self, model, admin_site):
        super(UptimeMonitoringAdmin, self).__init__(model, admin_site)
