import logging

from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import path

from valentina.celery import app
from validator.models import Settings
from django.contrib import messages

# see https://stackoverflow.com/a/53085512/
class SystemSettingsAdmin(ModelAdmin):

    __logger = logging.getLogger(__name__)

    fields = ['maintenance_mode', 'potential_maintenance', 'news', 'potential_maintenance_description', 'feed_link', 'sum_link']

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

        settings = Settings.load()
        s_form_class = super().get_form(request) # get the existing 'add' form class from the ModelAdmin
        s_form = None

        if(request.method == 'POST'):
            s_form = s_form_class(data=request.POST) # use the add form for parsing
            if s_form.is_valid():
                s = s_form.save(commit=False)
                self.__logger.debug('Saving settings: {}'.format(s))
                s.save()
                messages.add_message(request, messages.INFO, 'Settings have been saved.')


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


        if not s_form:
            # this happens if we don't have errors from a previous POST request to show
            s_form = s_form_class(instance=settings) # instantiate form with existing settings

        context = {
            'workers' : workers,
            'settings_form': s_form,
            }
        return render(request, 'admin/system_settings.html', context)
