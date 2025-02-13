from django.contrib.auth import get_user_model

User = get_user_model()
from django import forms

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email',
                  'first_name',
                  'last_name',
                  'organisation',
                  'country',
                  'orcid',
                  ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
