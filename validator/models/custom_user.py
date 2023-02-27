import logging
from re import search as reg_search

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django_countries.fields import CountryField


class User(AbstractUser):
    NO_DATA = 'no_data'
    BASIC = 'basic'
    EXTENDED = 'extended'
    UNLIMITED = 'unlimited'

    DATA_SPACE_LEVELS = (
        (NO_DATA, 1),
        (BASIC, 5 * 10**9),
        (EXTENDED, 10 ** 10),
        (UNLIMITED, None)
    )

    __logger = logging.getLogger(__name__)
    id = models.AutoField(primary_key=True)
    organisation = models.CharField(max_length=50, blank=True)
    country = CountryField(blank=True, blank_label='Country')
    orcid = models.CharField(max_length=25, blank=True)
    data_space = models.CharField(max_length=25, null=False, blank=True, choices=DATA_SPACE_LEVELS, default=BASIC)

    def clean(self):
        super(User, self).clean()
        if self.orcid:
            r = reg_search(settings.ORICD_REGEX, self.orcid)
            if not r or len(r.groups()) < 1:
                raise ValidationError({'orcid': 'Invalid ORCID identifier.',})
