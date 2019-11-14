import logging

from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import path

from valentina.celery import app
from validator.models import Settings


# see https://stackoverflow.com/a/53085512/
class SystemSettingsAdmin(ModelAdmin):

    __logger = logging.getLogger(__name__)

    def __init__(self, model, admin_site):
        super(SystemSettingsAdmin, self).__init__(model, admin_site)

    def get_urls(self):
        urls = super(SystemSettingsAdmin, self).get_urls()

        new_urls = [
            path('', self.admin_site.admin_view(self.system_settings), name='system-settings'),
        ]
        return new_urls + urls

    @csrf_protect_m
    def system_settings(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied

        if(request.method == 'POST'):
            maintenance_mode = request.POST.get('maintenance_mode', '')
            if ( (maintenance_mode == 'True') or (maintenance_mode == 'False') ):
                settings = Settings.load()
                settings.maintenance_mode = maintenance_mode
                settings.save()
                return HttpResponse("Saved.", status=200)
            else:
                return HttpResponse("Invalid.", status=400)

        # workers=app.control.inspect().active_queues()
        # workers=app.control.inspect().hello('celery@kk5')
        # queues = app.control.inspect().active_queues().keys()

        workers = []
        try:
            queue_dict = app.control.inspect().active_queues()
            active_tasks = app.control.inspect().active()
            sched_tasks = app.control.inspect().scheduled()

            if queue_dict:
                for worker_name, worker_queues in queue_dict.items():
                    worker = {}
                    worker['name'] = worker_name
                    worker['queues'] = []
                    for q in worker_queues:
                        worker['queues'].append(q['name'])
                    workers.append(worker)

                for w in workers:
                    w['active_tasks'] = len(active_tasks[w['name']])
                    w['scheduled_tasks'] = len(sched_tasks[w['name']])
        except Exception  as cre:
            self.__logger.exception('Can\'t get queue information: ', cre)

        context = {
            'workers' : workers,
            'maintenance_mode' : Settings.load().maintenance_mode
            }
        return render(request, 'admin/system_settings.html', context)
