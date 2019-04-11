from django.forms.models import ModelChoiceIterator

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