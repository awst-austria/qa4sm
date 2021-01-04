from datetime import datetime
import logging
from multiprocessing import Process
from re import sub as regex_subs

from dateutil.tz import tzlocal
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import connections
from django.forms import formset_factory
from django.forms.models import ModelMultipleChoiceField
from django.http.response import HttpResponse
from django.http.response import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template import loader

from validator.forms import DatasetConfigurationForm, FilterCheckboxSelectMultiple,\
    ValidationRunForm, ParamFilterChoiceField, ParamFilterSelectMultiple
from validator.models import DataFilter, DatasetVersion
from validator.models import Dataset
from validator.models import Settings
from validator.models import ValidationRun
from validator.models import ISMNNetworks
from validator.validation import run_validation
import validator.validation.globals as val_globals
from validator.validation.validation import stop_running_validation


# see https://docs.djangoproject.com/en/2.1/topics/forms/formsets/
DatasetConfigurationFormSet = formset_factory(DatasetConfigurationForm, extra=0, max_num=5, min_num=1, validate_max=True, validate_min=True)

__logger = logging.getLogger(__name__)

@login_required(login_url='/login/')
def stop_validation(request, result_uuid):
    if request.method == "DELETE":
        validation_run = get_object_or_404(ValidationRun, pk=result_uuid)
        if(validation_run.user != request.user):
            return HttpResponse(status=403)

        stop_running_validation(result_uuid)
        return HttpResponse("Validation stopped.", status=200)

    return HttpResponse(status=405) # if we're not DELETEing, send back "Method not Allowed"

@login_required(login_url='/login/')
def validation(request):
    dc_prefix = 'datasets'
    ref_prefix = 'ref'

    # initial values
    valrun_uuid = request.GET.get("valrun_uuid", None)
    if valrun_uuid == None:
        ref_filters = DataFilter.objects.filter(name="FIL_ALL_VALID_RANGE")
        ref_dataset = Dataset.objects.get(short_name=val_globals.ISMN)
        data_filters = [DataFilter.objects.filter(name="FIL_ALL_VALID_RANGE")]
        data_datasets = [Dataset.objects.get(short_name=val_globals.C3S)]
        valrun_initial_values = None
    else:
        valrun = get_object_or_404(ValidationRun, pk=valrun_uuid)
        # initial settings for datasets
        ref_config = valrun.reference_configuration
        ref_filters = ref_config.filters.all()
        ref_dataset = ref_config.dataset
        data_configs = [dc for dc in valrun.dataset_configurations.all()
                        if dc.id != ref_config.id]
        data_filters = [dc.filters.all()[::-1] for dc in data_configs]
        data_datasets = [dc.dataset for dc in data_configs]

        # validation run settings
        valrun_initial_values = {}
        for field in ValidationRunForm.Meta.fields:
            valrun_initial_values[field] = getattr(valrun, field)

    data_initial_values = [{'filters': data_filters[i],
                            'dataset': data_datasets[i], }
                           for i in range(len(data_datasets))]
    ref_initial_values = {'filters': ref_filters,
                          'dataset': ref_dataset, }

    if request.method == "POST":
        if Settings.load().maintenance_mode:
            __logger.info('Redirecting to the validation page because the system is in maintenance mode.')
            return redirect('validation')

        # formset for data configurations for our new validation
        dc_formset = DatasetConfigurationFormSet(request.POST, prefix=dc_prefix, initial=data_initial_values)

        ## apparently, a missing management form on the formset is a reason to throw a hissy fit err...
        ## ValidationError - instead of just appending it to dc_formset.non_form_errors. Whatever...
        try:
            dc_formset.is_valid()
        except ValidationError as e:
            __logger.exception(e)
            if e.code == 'missing_management_form':
                return HttpResponseBadRequest('Not a valid request: ' + e.message)

        # form for the reference configuration
        ref_dc_form = DatasetConfigurationForm(request.POST, prefix=ref_prefix, is_reference=True, initial=ref_initial_values)
        # form for the rest of the validation parameters
        val_form = ValidationRunForm(request.POST, initial=valrun_initial_values)
        if val_form.is_valid() and dc_formset.is_valid() and ref_dc_form.is_valid():
            newrun = val_form.save(commit=False)
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
            run_id = newrun.id

            # attach all dataset configurations to the validation and save them
            for dc_form in dc_formset:
                dc = dc_form.save(commit=False)
                dc.validation = newrun
                dc.save()
                dc_form.save_m2m() # save many-to-many related objects, e.g. filters. If you don't do this, filters won't get saved!

            # also attach the reference config
            ref_dc = ref_dc_form.save(commit=False)
            ref_dc.validation = newrun
            ref_dc.save()
            ref_dc_form.save_m2m() # save many-to-many related objects, e.g. filters. If you don't do this, filters won't get saved!

            newrun.reference_configuration = ref_dc

            ## determine the scaling reference. For intercomparison, only the reference makes sense. Otherwise let the user pick.
            if ((len(dc_formset) == 1) and
                (val_form.cleaned_data['scaling_ref'] == ValidationRun.SCALE_TO_DATA)):
                newrun.scaling_ref = dc
            else:
                newrun.scaling_ref = ref_dc

            newrun.save()

            # need to close all db connections before forking, see
            # https://stackoverflow.com/questions/8242837/django-multiprocessing-and-database-connections/10684672#10684672
            connections.close_all()

            p = Process(target=run_validation, kwargs={"validation_id": run_id})
            p.start()

            return redirect('result', result_uuid=run_id)
        else:
            __logger.error("Errors in validation form {}\n{}\n{}".format(val_form.errors, dc_formset.errors, ref_dc_form.errors))
    else:
        val_form = ValidationRunForm(initial=valrun_initial_values)
        dc_formset = DatasetConfigurationFormSet(prefix=dc_prefix, initial=data_initial_values)
        ref_dc_form = DatasetConfigurationForm(prefix=ref_prefix, is_reference=True, initial=ref_initial_values)
        # ref_dc_form.


    return render(request, 'validator/validate.html', {'val_form': val_form, 'dc_formset': dc_formset, 'ref_dc_form': ref_dc_form, 'maintenance_mode':Settings.load().maintenance_mode})


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
def __render_filters(filters, filter_widget_id, parametrised = False):
    widget_name = regex_subs(r'^id_', '', filter_widget_id)
    if parametrised:
        filter_field = ParamFilterChoiceField(widget=ParamFilterSelectMultiple, queryset=filters, required=False)
    else:
        filter_field = ModelMultipleChoiceField(widget=FilterCheckboxSelectMultiple, queryset=filters, required=False)

    preselected = None
    if filters:
        # pre-select the first filter
        preselected = filters[0].id

    filter_html = filter_field.widget.render(
        name=widget_name,
        value=preselected,
        attrs={'id': filter_widget_id})
    return filter_html

## returns the options for the variable and version select dropdowns and the filter checkboxes based on the selected dataset
@login_required(login_url='/login/')
def ajax_get_dataset_options(request):
    selected_dataset_name = request.GET.get('dataset_id')
    filter_widget_id = request.GET.get('filter_widget_id')
    param_filter_widget_id = request.GET.get('param_filter_widget_id')

    try:
        selected_dataset = Dataset.objects.get(pk=selected_dataset_name)
    except:
        return HttpResponseBadRequest("Not a valid dataset")

    response_data = {
        'versions': __render_options(selected_dataset.versions.all().order_by('-pretty_name')),
        'variables': __render_options(selected_dataset.variables.all().order_by('id')),
        'filters': __render_filters(selected_dataset.filters.filter(parameterised=False), filter_widget_id, parametrised = False),
        'paramfilters': __render_filters(selected_dataset.filters.filter(parameterised=True), param_filter_widget_id, parametrised = True),
        }

    return JsonResponse(response_data)

@login_required(login_url='/login/')
def ajax_get_version_id(request):
    version_id = request.GET.get('version_id')
    try:
        version = DatasetVersion.objects.get(pk=int(version_id))
        networks = version.network_version.all()
        continents = networks.values('continent').distinct().values_list('continent', flat=True)
        network_dict =  {continent: [(network.name, network.country, network.number_of_stations) for network in networks.filter(continent=continent)] for continent in continents}
    except:
        return HttpResponseBadRequest("Not a valid dataset version")

    response_data = {
        'network': network_dict
        }

    return JsonResponse(response_data)
