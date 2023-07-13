import logging
from re import search as reg_search

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django_countries.fields import CountryField
# from validator.models import UserDatasetFile


class User(AbstractUser):
    NO_DATA = 'no_data'
    BASIC = 'basic'
    EXTENDED = 'extended'
    UNLIMITED = 'unlimited'
    LARGE = 'large'

    DATA_SPACE_LEVELS = (
        (NO_DATA, 1),
        (BASIC, 5 * 10**9),
        (EXTENDED, 10 ** 10),
        (LARGE, 200 * 10**9),
        (UNLIMITED, None)
    )

    __logger = logging.getLogger(__name__)
    id = models.AutoField(primary_key=True)
    organisation = models.CharField(max_length=50, blank=True)
    country = CountryField(blank=True, blank_label='Country')
    orcid = models.CharField(max_length=25, blank=True)
    space_limit = models.CharField(max_length=25, null=False, blank=True, choices=DATA_SPACE_LEVELS, default=BASIC)

    @property
    def space_limit_value(self):
        # this property is added to be able to use it in api
        return self.get_space_limit_display()
    @property
    def space_left(self):
        if self.get_space_limit_display():
            used_space = sum(file.file_size for file in self.user_datasets.all())
            return self.get_space_limit_display() - used_space

        return

    def clean(self):
        super(User, self).clean()
        if self.orcid:
            r = reg_search(settings.ORICD_REGEX, self.orcid)
            if not r or len(r.groups()) < 1:
                raise ValidationError({'orcid': 'Invalid ORCID identifier.',})
