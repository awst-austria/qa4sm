from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField


class User(AbstractUser):
    organisation = models.CharField(max_length=50, blank=True)
    country = CountryField(blank=True, blank_label='Country')
