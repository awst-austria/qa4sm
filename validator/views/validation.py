from datetime import datetime
from multiprocessing import Process

from dateutil.tz import tzlocal
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from validator.forms import ValidationRunForm
from validator.validation import run_validation
from django.db import connections
import logging
from django.http.response import HttpResponseBadRequest, JsonResponse
from django.template import loader
from validator.forms.validation_run import FilterCheckboxSelectMultiple
from django.forms.models import ModelMultipleChoiceField
from validator.models import Dataset
from validator.models import Settings


__logger = logging.getLogger(__name__)


## TODO: find nicer way to restrict access (not repeating login_required on every view)
@login_required(login_url='/login/')
def validation(request):
    if request.method == "POST":
        if Settings.load().maintenance_mode:
            __logger.info('Redirecting to the validation page because the system is in maintenance mode.')
            return redirect('validation')

        form = ValidationRunForm(request.POST)
        if form.is_valid():
            newrun = form.save(commit=False)
            newrun.user = request.user
            newrun.start_time = datetime.now(tzlocal())

            if newrun.interval_from is not None:
                # truncate time
                newrun.interval_from = datetime(year=newrun.interval_from.year,
                                                month=newrun.interval_from.month,
                                                day=newrun.interval_from.day,
                                                tzinfo=newrun.interval_from.tzinfo)
            if newrun.interval_to is not None:
                # truncate time and go to 1 sec before midnight
                newrun.interval_to = datetime(year=newrun.interval_to.year,
                                                month=newrun.interval_to.month,
                                                day=newrun.interval_to.day,
                                                hour=23,
                                                minute=59,
                                                second=59,
                                                microsecond=999999,
                                                tzinfo=newrun.interval_to.tzinfo)
            newrun.save() # save the validation run
            form.save_m2m() # save many-to-many related objects, e.g. filters. If you don't do this, filters won't get saved!
            run_id = newrun.id

            # need to close all db connections before forking, see
            # https://stackoverflow.com/questions/8242837/django-multiprocessing-and-database-connections/10684672#10684672
            connections.close_all()

            ## TODO: Check if we want to use celery: http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#tut-celery
            p = Process(target=run_validation, kwargs={"validation_id": run_id})
            p.start()

            return redirect('result', result_uuid=run_id)
        else:
            __logger.error("Errors in validation form {}".format(form.errors))
    else:
        form = ValidationRunForm()

    return render(request, 'validator/validate.html', {'form': form,'maintenance_mode':Settings.load().maintenance_mode})


## Ajax stuff required for validation view

## render string options as html
def __render_options(entity_list):
    widgets = []
    for entity in entity_list:
        widget = {
            'value' : entity.id,
            'label': entity.pretty_name,
            }
        widgets.append(widget)

    content = loader.render_to_string('widgets/select_options.html', {'widgets': widgets})
    return content

# render filters as html checkboxes with descriptions
def __render_filters(filters, selected_type):
    widget_name='data_filters'
    widget_id='id_data_filters'
    if selected_type == 'ref':
        widget_name='ref_filters'
        widget_id='id_ref_filters'

    filter_field = ModelMultipleChoiceField(widget=FilterCheckboxSelectMultiple, queryset=filters, required=False)
    filter_html = filter_field.widget.render(
        name=widget_name,
        value=filters[0].id, # this pre-selects the first filter in the form
        attrs={'id': widget_id})
    return filter_html

## returns the options for the variable and version select dropdowns and the filter checkboxes based on the selected dataset
@login_required(login_url='/login/')
def ajax_get_dataset_options(request):
    selected_dataset_name = request.GET.get('dataset_id')
    selected_type = request.GET.get('dataset_type')

    try:
        selected_dataset = Dataset.objects.get(pk=selected_dataset_name)
    except:
        return HttpResponseBadRequest("Not a valid dataset")

    # ignore pranksters who send other types than 'ref' or 'data'
    if selected_type != 'ref':
        selected_type = 'data'

    response_data = {
        'versions': __render_options(selected_dataset.versions.all().order_by('pretty_name')),
        'variables': __render_options(selected_dataset.variables.all()),
        'filters': __render_filters(selected_dataset.filters.all(), selected_type),
        }

    return JsonResponse(response_data)
