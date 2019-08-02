from datetime import datetime

from django.forms.models import ModelChoiceIterator
from pytz import UTC

import django.forms as forms


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