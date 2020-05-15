from django.contrib.auth import get_user_model, password_validation
User = get_user_model()
from django.contrib.auth.forms import UserCreationForm


class UserProfileForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username',
                  'password1',
                  'password2',
                  'email',
                  'first_name',
                  'last_name',
                  'organisation',
                  'country',
                  'orcid',
                  ]

    def clean(self):
        form_data = self.cleaned_data
        if (('password2' not in form_data) or
            (form_data['password1'] != form_data['password2'])):   # Workaround for missing password2 key
            self._errors["password1"] = ["Passwords do not match"] # Will raise an error message
            del form_data['password1']
        return form_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].help_text = ' '.join(password_validation.password_validators_help_texts())
        self.fields['email'].required = True
        self.fields['email'].help_text = 'Required. A valid email address where you can receive notifications about validations.'

        self.fields['first_name'].help_text = 'Optional.'
        self.fields['last_name'].help_text = 'Optional.'
        self.fields['organisation'].help_text = 'Optional. The organisation (university, company, etc.) you work for or represent.'
        self.fields['country'].help_text = 'Optional. The country where your organisation (or you) resides.'
        self.fields['orcid'].help_text = 'Optional. Your ORCID identifier from https://orcid.org/, e.g. 0000-0002-1825-0097. Will be used to identify you as the author if you publish results to zenodo through QA4SM.'
        self.fields['orcid'].label = 'ORCID'
