from django.contrib.auth import get_user_model, password_validation
User = get_user_model()
from django.contrib.auth.forms import UserCreationForm

import django.forms as forms


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
                  'country',]

<<<<<<< HEAD
    def clean(self):
        form_data = self.cleaned_data
        if form_data['password1'] != form_data['password2']:
            self._errors["password1"] = ["Password do not match"] # Will raise a error message
            del form_data['password1']
        return form_data
    
    
=======
>>>>>>> 192a82a053f2bd402689e8a5302f45dcdd332440
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].help_text = ' '.join(password_validation.password_validators_help_texts())
        self.fields['email'].required = True
        self.fields['email'].help_text = 'Required. A valid email address where you can receive notifications about validations.'

        self.fields['first_name'].help_text = 'Optional.'
        self.fields['last_name'].help_text = 'Optional.'
        self.fields['organisation'].help_text = 'Optional. The organisation (university, company, etc.) you work for or represent.'
        self.fields['country'].help_text = 'Optional. The country where your organisation (or you) resides.'
