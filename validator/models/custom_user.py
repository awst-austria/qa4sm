import logging
from re import search as reg_search

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django_countries.fields import CountryField
from validator.models import DataManagementGroup


class User(AbstractUser):
    NO_DATA = 'no_data'
    BASIC = 'basic'
    EXTENDED = 'extended'
    ACTIVE = 'active'
    REGULAR = 'regular'
    FREQUENT = 'frequent'
    POWER_USER = 'power_user'
    LARGE = 'large'
    UNLIMITED = 'unlimited'
    LARGE = 'large'
    # make email unique

    DATA_SPACE_LEVELS = (
        (NO_DATA, 1),  # 1 byte
        (BASIC, 5 * 10**9),  # 5 GB
        (EXTENDED, 10**10),  # 10 GB
        (ACTIVE, 20 * 10**9),  # 20 GB - Active users
        (REGULAR, 50 * 10**9),  # 50 GB - Regular users
        (FREQUENT, 75 * 10**9),  # 75 GB - Frequent users
        (POWER_USER, 100 * 10**9),  # 100 GB - Power users
        (LARGE, 200 * 10**9),  # 200 GB
        (UNLIMITED, None)  # No limit
    )

    __logger = logging.getLogger(__name__)
    id = models.AutoField(primary_key=True)
    organisation = models.CharField(max_length=50, blank=True)
    country = CountryField(blank=True, blank_label='Country')
    orcid = models.CharField(max_length=25, blank=True)
    space_limit = models.CharField(max_length=25,
                                   null=False,
                                   blank=True,
                                   choices=DATA_SPACE_LEVELS,
                                   default=BASIC)

    @property
    def space_limit_value(self):
        # this property is added to be able to use it in api
        return self.get_space_limit_display()

    @property
    def used_space(self):
        return sum(file.file_size for file in self.user_datasets.all()
                   if file.file)

    @property
    def space_left(self):
        if self.get_space_limit_display():
            return self.get_space_limit_display() - self.used_space

        return

    def data_management_groups(self):
        return DataManagementGroup.objects.filter(user=self)

    @property
    def belongs_to_data_management_groups(self):
        return len(self.data_management_groups()) > 0

    def clean(self):
        super(User, self).clean()
        if self.orcid:
            r = reg_search(settings.ORICD_REGEX, self.orcid)
            if not r or len(r.groups()) < 1:
                raise ValidationError({
                    'orcid': 'Invalid ORCID identifier.',
                })
