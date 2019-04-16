from datetime import datetime

from django.contrib.auth import get_user_model
User = get_user_model()

import django.forms as forms
from validator.models import ValidationRun


## See https://simpleisbetterthancomplex.com/article/2017/08/19/how-to-render-django-form-manually.html
## To figure out how to make one dropdown dependent on the selection of another, see:
## https://simpleisbetterthancomplex.com/tutorial/2018/01/29/how-to-implement-dependent-or-chained-dropdown-list-with-django.html
class ValidationRunForm(forms.ModelForm):

    class Meta:
        model = ValidationRun
        ## specify the fields of the model that should be included in the form:
        fields = [
            'interval_from',
            'interval_to',
            #'scaling_ref',
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
