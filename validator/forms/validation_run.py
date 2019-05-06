from datetime import datetime

from django.contrib.auth import get_user_model
from validator.models import Dataset
User = get_user_model()
from django.forms.models import ModelMultipleChoiceField, ModelChoiceIterator

import django.forms as forms
from validator.models import ValidationRun
from validator.models.filter import DataFilter
from validator.validation import globals as val_globals


class FilterCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Hackaround to render the data filters checkboxes with help texts and correct
    formatting.
    """
    option_template_name = 'widgets/filter_checkbox_option.html'
    template_name = 'widgets/filter_checkbox_select.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        duper = super(forms.CheckboxSelectMultiple, self).create_option(name, value, label, selected, index, subindex, attrs)

        if isinstance(self.choices, ModelChoiceIterator):
            for fil in self.choices.queryset:
                if fil.id == value:
                    duper['label'] = fil.description
                    duper['help_text'] = fil.help_text
                    break

        return duper

# https://docs.djangoproject.com/en/2.2/ref/forms/fields/#django.forms.ModelChoiceField
# make sure the pretty name is used in the dropdown for the dataset selection
class DatasetChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.pretty_name

## See https://simpleisbetterthancomplex.com/article/2017/08/19/how-to-render-django-form-manually.html
## To figure out how to make one dropdown dependent on the selection of another, see:
## https://simpleisbetterthancomplex.com/tutorial/2018/01/29/how-to-implement-dependent-or-chained-dropdown-list-with-django.html
class ValidationRunForm(forms.ModelForm):

    filter_data = forms.BooleanField(initial=True, required=False, label='Filter data')
    filter_ref = forms.BooleanField(initial=True, required=False, label='Filter reference')

    data_dataset = DatasetChoiceField(queryset=Dataset.objects.filter(is_reference=False), required=True)
    ref_dataset = DatasetChoiceField(queryset=Dataset.objects.filter(is_reference=True), required=True)

    data_filters = ModelMultipleChoiceField(widget=FilterCheckboxSelectMultiple, queryset=DataFilter.objects.all(), required=False)
    ref_filters = ModelMultipleChoiceField(widget=FilterCheckboxSelectMultiple, queryset=DataFilter.objects.all(), required=False)
    # see https://stackoverflow.com/questions/2216974/django-modelform-for-many-to-many-fields/2264722#2264722
    # and https://docs.djangoproject.com/en/2.1/ref/forms/fields/#django.forms.ModelMultipleChoiceField

    class Meta:
        model = ValidationRun
        ## specify the fields of the model that should be included in the form:
        fields = [
            'data_dataset',
            'data_version',
            'data_variable',
            'ref_dataset',
            'ref_version',
            'ref_variable',
            'interval_from',
            'interval_to',
            'filter_data',
            'data_filters',
            'filter_ref',
            'ref_filters',
            'scaling_ref',
            'scaling_method',
            'name_tag',
            ]

    def __init__(self, *args, **kwargs):
        super(ValidationRunForm, self).__init__(*args, **kwargs)
        ## Specifiy the fields of the model that are OPTIONAL in the form:
        self.fields['interval_from'].required = False
        self.fields['interval_to'].required = False

        ## give default/initial values to widgets
        self.fields['interval_from'].initial = datetime(1978, 1, 1).strftime('%Y-%m-%d')
        self.fields['interval_to'].initial = datetime.now().strftime('%Y-%m-%d')
        self.fields['data_filters'].initial = DataFilter.objects.get(name='FIL_ALL_VALID_RANGE')
        self.fields['ref_filters'].initial = DataFilter.objects.get(name='FIL_ALL_VALID_RANGE')

        self.fields['data_dataset'].initial = Dataset.objects.get(short_name=val_globals.C3S)
        self.fields['ref_dataset'].initial = Dataset.objects.get(short_name=val_globals.ISMN)

    def clean(self):
        cleaned_data = super(ValidationRunForm, self).clean()

        # this shouldn't be necessary because the values of disabled checkboxes in HTML forms
        # don't get submitted, but let's err on the side of caution...
        if not cleaned_data['filter_data']:
            cleaned_data['data_filters'] = DataFilter.objects.none()

        if not cleaned_data['filter_ref']:
            cleaned_data['ref_filters'] = DataFilter.objects.none()

        return cleaned_data
