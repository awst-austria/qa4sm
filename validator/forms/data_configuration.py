from django.forms.models import ModelMultipleChoiceField

import django.forms as forms
from validator.forms import FilterCheckboxSelectMultiple
from validator.models import Dataset
from validator.models import DatasetConfiguration
from validator.models.filter import DataFilter

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
            ]

    dataset = DatasetChoiceField(queryset=Dataset.objects.none(), required=True)

    filter_dataset = forms.BooleanField(initial=True, required=False, label='Filter dataset')

    # if you change this field, be sure to adapt validator.views.validation.__render_filters
    filters = ModelMultipleChoiceField(widget=FilterCheckboxSelectMultiple, queryset=DataFilter.objects.all(), required=False)

    # see https://stackoverflow.com/questions/2216974/django-modelform-for-many-to-many-fields/2264722#2264722
    # and https://docs.djangoproject.com/en/2.1/ref/forms/fields/#django.forms.ModelMultipleChoiceField

    ## if you want to create a dataset config form for reference datasets, pass in parameter is_reference=True
    def __init__(self, *args, is_reference=False, **kwargs):
        super(DatasetConfigurationForm, self).__init__(*args, **kwargs)
        self.fields["dataset"].queryset = Dataset.objects.filter(is_reference=is_reference)

    def clean(self):
        cleaned_data = super(DatasetConfigurationForm, self).clean()

        # this shouldn't be necessary because the values of disabled checkboxes in HTML forms
        # don't get submitted, but let's err on the side of caution...
        if not cleaned_data['filter_dataset']:
            cleaned_data['filters'] = DataFilter.objects.none()

        return cleaned_data
