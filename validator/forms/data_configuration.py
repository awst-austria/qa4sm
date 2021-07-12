from django.forms.models import ModelMultipleChoiceField

import django.forms as forms
from validator.forms import FilterCheckboxSelectMultiple
from validator.models import Dataset
from validator.models import DatasetConfiguration
from validator.models.filter import DataFilter
from validator.forms.custom_widgets import ParamFilterChoiceField,\
    ParamFilterSelectMultiple
from validator.validation.globals import NOT_AS_REFERENCE

# https://docs.djangoproject.com/en/2.2/ref/forms/fields/#django.forms.ModelChoiceField
# make sure the pretty name is used in the dropdown for the dataset selection
class DatasetChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.pretty_name

## To figure out how to make one dropdown dependent on the selection of another, see:
## https://simpleisbetterthancomplex.com/tutorial/2018/01/29/how-to-implement-dependent-or-chained-dropdown-list-with-django.html
class DatasetConfigurationForm(forms.ModelForm):
    class Meta:
        model = DatasetConfiguration

        fields = [
            'dataset',
            'version',
            'variable',
            'filters',
            'parametrised_filters',
            ]

    dataset = DatasetChoiceField(queryset=Dataset.objects.none(), required=True)

    filter_dataset = forms.BooleanField(initial=True, required=False, label='Filter dataset')

    # if you change this field, be sure to adapt validator.views.validation.__render_filters
    filters = ModelMultipleChoiceField(widget=FilterCheckboxSelectMultiple, queryset=DataFilter.objects.filter(parameterised=False), required=False)

    # see https://stackoverflow.com/questions/2216974/django-modelform-for-many-to-many-fields/2264722#2264722
    # and https://docs.djangoproject.com/en/2.1/ref/forms/fields/#django.forms.ModelMultipleChoiceField

    # if you change this, be sure to adapt _save_m2m and validator.views.validation.__render_filters
    parametrised_filters = ParamFilterChoiceField(widget=ParamFilterSelectMultiple, queryset=DataFilter.objects.filter(parameterised=True), required=False)

    ## if you want to create a dataset config form for reference datasets, pass in parameter is_reference=True
    def __init__(self, *args, is_reference=False, **kwargs):
        super(DatasetConfigurationForm, self).__init__(*args, **kwargs)

        if is_reference:
            # self.fields["dataset"].queryset = Dataset.objects.all()
            # temporarily SMOS, SMAP and ASCAT are removed from the reference list
            self.fields["dataset"].queryset = Dataset.objects.exclude(short_name__in=NOT_AS_REFERENCE)
        else:
            self.fields["dataset"].queryset = Dataset.objects.filter(is_only_reference=is_reference)

        for key in ["dataset", "version", "variable"]:
            self.fields[key].initial = self.get_initial_for_field(
                self.fields[key], key
            )

        # This translates the initial filter list to a string of filter ids
        # separated by an underscore. This string is passed to the ajax call
        # `ajax_change_dataset` in validate.html, and then further passed to
        # `ajax_get_dataset_options` in validation.py.
        if "filters" in self.initial:
            self.initial_filters = ",".join(map(
                lambda x: str(getattr(x, "id")), list(self.initial["filters"])
            ))
        else:
            self.initial_filters = ""
        if "parametrised_filters" in self.initial:
            self.initial_paramfilters = ",".join(map(
                lambda x: str(getattr(x, "id")),
                list(self.initial["parametrised_filters"])
            ))
            if "paramfilter_params" in self.initial:
                self.initial_paramfilter_params = ";".join(
                    self.initial["paramfilter_params"]
                )
            else:
                self.initial_paramfilter_params = ""
        else:
            self.initial_paramfilters = ""
            self.initial_paramfilter_params = ""
        # do the same for version and variable
        if "version" in self.initial:
            self.initial_version = str(self.initial["version"].id)
        else:
            self.initial_version = ""
        if "variable" in self.initial:
            self.initial_variable = str(self.initial["variable"].id)
        else:
            self.initial_variable = ""

    def _save_m2m(self):
        # treat the parametrised filters separately, remove them now, save after calling super
        param_filters = None
        if('parametrised_filters' in self.cleaned_data and self.cleaned_data['parametrised_filters']):
            param_filters = self.cleaned_data['parametrised_filters']
            self.cleaned_data['parametrised_filters'] = []

        super(DatasetConfigurationForm, self)._save_m2m()

        # apparently, the unsaved ParametrisedFilter objects need to have save called on them explicitly, so do that
        # https://stackoverflow.com/questions/31862599/how-to-save-a-manytomany-field-with-a-through-relationship/31863016#31863016
        if param_filters:
            for pf in param_filters:
                pf.dataset_config = self.instance
                pf.save()

    def clean(self):
        cleaned_data = super(DatasetConfigurationForm, self).clean()

        # this shouldn't be necessary because the values of disabled checkboxes in HTML forms
        # don't get submitted, but let's err on the side of caution...
        if not cleaned_data['filter_dataset']:
            cleaned_data['filters'] = DataFilter.objects.none()
            cleaned_data['parametrised_filters'] = []

        return cleaned_data
