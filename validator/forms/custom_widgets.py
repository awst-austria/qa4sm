from datetime import datetime

from django.forms.models import ModelChoiceIterator, ModelMultipleChoiceField
from pytz import UTC

import django.forms as forms
from validator.models import ParametrisedFilter


class FilterCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Hackaround to render the data filters checkboxes with help texts and correct
    formatting.
    """
    option_template_name = 'widgets/filter_checkbox_option.html'
    template_name = 'widgets/filter_checkbox_select.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        duper = super(FilterCheckboxSelectMultiple, self).create_option(name, value, label, selected, index, subindex, attrs)

        if isinstance(self.choices, ModelChoiceIterator):
            for fil in self.choices.queryset:
                if fil.id == value:
                    duper['label'] = fil.description
                    duper['help_text'] = fil.help_text
                    duper['parameterised'] = fil.parameterised
                    duper['dialog_name'] = fil.dialog_name
                    duper['default_parameter'] = fil.default_parameter
                    duper['to_include'] = fil.to_include
                    duper['to_exclude'] = fil.to_exclude
                    duper['threshold'] = fil.threshold,
                    duper['default_threshold'] = fil.default_threshold,
                    duper['min_threshold'] = fil.min_threshold,
                    duper['max_threshold'] = fil.max_threshold,
                    if ("initial_params" in attrs
                            and attrs["initial_params"] is not None):
                        duper["initial_params"] = attrs["initial_params"][index]
                    else:
                        duper["initial_params"] = fil.default_parameter
                    break

        return duper

class ParamFilterSelectMultiple(FilterCheckboxSelectMultiple):
    # match selected filters with their parameters; parameters must be passed in fields with the same name with '_params' appended
    def value_from_datadict(self, data, files, name):
        params_name = name + "_params"
        filter_ids = super(FilterCheckboxSelectMultiple, self).value_from_datadict(data, files, name)
        parameters = super(FilterCheckboxSelectMultiple, self).value_from_datadict(data, files, params_name)
        if filter_ids and parameters:
            return list(zip(filter_ids, parameters))
        else:
            return (None, None)

class ParamFilterChoiceField(ModelMultipleChoiceField):

    ## return new (unsaved) ParametrisedFilter objects; their dataset_config property needs
    ## to be set later, e.g. in the using form's _save_m2m method
    def clean(self, value):
        ## assume that we get a list of tuples of filter id and parameter strings, e.g.:
        ## [('17', 'temp > 0'), ('18', 'RISMA, SCAN, SNOTEL')]
        if isinstance(value, list):
            # unzip again
            filter_ids, params = list(zip(*value))

            # clean the filter_ids, returns queryset of filters
            filters = super(ParamFilterChoiceField, self).clean(filter_ids)

            # create new ParametrisedFilter objects (but don't save yet)
            param_filters = []
            for f, p in zip(filters, params):
                param_filters.append( ParametrisedFilter(filter=f, parameters=p) )

            return param_filters
        else:
            return []


class YearChoiceField(forms.fields.ChoiceField):
    """
    Allows the user to select a year from a range of years.
    Initial value is the start or end of the range, depending on is_interval_start.
    Returns Jan 1st or Dec 31st of that year, depending on is_interval_start.
    """

    def __init__(self, is_interval_start=True, start_year=1978, end_year=None, *args, **kwargs):
        self.is_interval_start = is_interval_start

        if not end_year:
            end_year = datetime.now().year

        year_range = range(start_year, end_year + 1)
        init_val = start_year if self.is_interval_start else (end_year -1) ## default is from start of range until last year

        super(YearChoiceField, self).__init__(choices = list(zip(year_range, year_range)), initial=init_val, *args, **kwargs)

    def clean(self, value):
        v = super(YearChoiceField, self).clean(value)

        if not v:
            return None

        if self.is_interval_start:
            v_date = datetime(year=int(v), month=1, day=1, hour=0, minute=0, second=0, tzinfo=UTC)
        else:
            v_date = datetime(year=int(v), month=12, day=31, hour=23, minute=59, second=59, tzinfo=UTC)

        return v_date
