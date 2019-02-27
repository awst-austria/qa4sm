from django.contrib.auth import get_user_model, password_validation
User = get_user_model()
from django.contrib.auth.forms import UserCreationForm

import django.forms as forms


class SignUpForm(UserCreationForm):
    terms_consent = forms.BooleanField(required=True,
                                       error_messages={'required': 'You need to accept the terms and conditions to create an account.'},
                                       help_text='You need to accept the terms and conditions to create an account.')

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
                  'terms_consent',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ' '.join(password_validation.password_validators_help_texts())
        self.fields['email'].required = True
        self.fields['email'].help_text = 'Required. A valid email address where you can receive notifications about validations.'

        self.fields['first_name'].help_text = 'Optional.'
        self.fields['last_name'].help_text = 'Optional.'
        self.fields['organisation'].help_text = 'Optional. The organisation (university, company, etc.) you work for or represent.'
        self.fields['country'].help_text = 'Optional. The country where your organisation (or you) resides.'
