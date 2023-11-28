from django.contrib.admin.options import ModelAdmin
from validator.models import ValidationRun


class CeleryTasksAdmin(ModelAdmin):
    list_display = ('validation_id', 'celery_task_id', 'validation_date')
    ordering = ('validation_id',)

    def validation_date(self, obj):
        try:
            val = ValidationRun.objects.get(pk=obj.validation_id)
            return val.start_time
        except:
            return
