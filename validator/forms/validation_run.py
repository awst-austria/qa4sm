from datetime import datetime

from django.contrib.auth import get_user_model
User = get_user_model()

import django.forms as forms
from validator.forms import YearChoiceField
from validator.models import ValidationRun


## See https://simpleisbetterthancomplex.com/article/2017/08/19/how-to-render-django-form-manually.html
class ValidationRunForm(forms.ModelForm):

    class Meta:
        model = ValidationRun
        ## specify the fields of the model that should be included in the form:
        fields = [
            'interval_from',
            'interval_to',
            'scaling_method',
            'name_tag',
            'anomalies',
            'anomalies_from',
            'anomalies_to',
            'min_lat',
            'min_lon',
            'max_lat',
            'max_lon',
            'tcol',
            ]

    scaling_ref = forms.fields.ChoiceField(choices=[(ValidationRun.SCALE_TO_REF, 'Reference'), (ValidationRun.SCALE_TO_DATA, 'Data'), ])

    anomalies_from = YearChoiceField(required=False, is_interval_start=True)
    anomalies_to = YearChoiceField(required=False, is_interval_start=False)

    def __init__(self, *args, **kwargs):
        super(ValidationRunForm, self).__init__(*args, **kwargs)
        ## Specifiy the fields of the model that are OPTIONAL in the form:
        self.fields['interval_from'].required = False
        self.fields['interval_to'].required = False
        self.fields['anomalies'].required = False
        self.fields['min_lat'].required = False
        self.fields['min_lon'].required = False
        self.fields['max_lat'].required = False
        self.fields['max_lon'].required = False

        # default/initial values
        self.fields['min_lat'].initial = 34.00
        self.fields['min_lon'].initial = -11.20
        self.fields['max_lat'].initial = 71.60
        self.fields['max_lon'].initial = 48.30
        self.fields['interval_from'].initial = datetime(1978, 1, 1).strftime('%Y-%m-%d')
        self.fields['interval_to'].initial = datetime.now().strftime('%Y-%m-%d')

        # in case the form got passed initial values, use them instead
        for name in self.fields:
            self.fields[name].initial = self.get_initial_for_field(
                self.fields[name], name
            )

    def clean(self):
        values = super(ValidationRunForm, self).clean()
        if(('anomalies' in values) and (values['anomalies'] != ValidationRun.CLIMATOLOGY)):
            values['anomalies_from'] = None
            values['anomalies_to'] = None
        return values
