from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AbstractUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django.http import JsonResponse
from django_countries import countries


@api_view(['GET'])
@permission_classes([AllowAny])
def get_list_of_countries(request):
    country_dict = countries.countries
    response = [{'code': key, 'name': country_dict[key]} for key in country_dict]
    return JsonResponse(response, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_form_help(request):
    user_form_info = [
        {'field': 'username',
         'help_text': AbstractUser()._meta.get_field('username').help_text,
         'required': True},
        {'field': 'password',
         'help_text': ' '.join(password_validation.password_validators_help_texts()),
         'required': True},
        {'field': 'password2',
         'help_text': UserCreationForm().fields['password2'].help_text,
         'required': True},
        {'field': 'email',
         'help_text': 'Required. A valid email address where you can receive notifications about validations.',
         'required': True},
        {'field': 'first_name',
         'help_text': 'Optional.',
         'required': False},
        {'field': 'last_name',
         'help_text': 'Optional.',
         'required': False},
        {'field': 'organisation',
         'help_text': 'Optional. The organisation (university, company, etc.) you work for or represent.',
         'required': False},
        {'field': 'country',
         'help_text': 'Optional. The country where your organisation (or you) resides.',
         'required': False},
        {'field': 'orcid',
         'help_text': 'Optional. Your ORCID identifier from https://orcid.org/, e.g. 0000-0002-1825-0097. Will be used '
                      'to identify you as the author if you publish results to zenodo through QA4SM.',
         'required': False},
    ]
    return JsonResponse(user_form_info, safe=False)