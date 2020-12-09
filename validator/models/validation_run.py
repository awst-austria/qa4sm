from datetime import timedelta
from os import path
from re import sub as regex_sub
from shutil import rmtree
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils import timezone

from validator.models import DatasetConfiguration


class ValidationRun(models.Model):

    ## scaling methods
    MIN_MAX = 'min_max'
    LINREG = 'linreg'
    MEAN_STD = 'mean_std'
    LIN_CDF_MATCH = 'lin_cdf_match'
    CDF_MATCH = 'cdf_match'
    NO_SCALING = 'none'

    SCALING_METHODS = (
        (NO_SCALING, 'No scaling'),
        (MIN_MAX, 'Min/Max'),
        (LINREG, 'Linear regression'),
        (MEAN_STD, 'Mean/standard deviation'),
#         (LIN_CDF_MATCH, 'CDF matching with linear interpolation'),
#         (CDF_MATCH, 'CDF matching with 5-th order spline fitting'),
        )

    ## scale to
    SCALE_TO_REF = 'ref'
    SCALE_TO_DATA = 'data'

    ## anomalies
    MOVING_AVG_35_D = "moving_avg_35_d"
    CLIMATOLOGY = "climatology"
    NO_ANOM = "none"
    ANOMALIES_METHODS = (
        (NO_ANOM, 'Do not calculate'),
        (MOVING_AVG_35_D, '35 day moving average'),
        (CLIMATOLOGY, 'Climatology'),
        )

    ## fields

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_tag = models.CharField(max_length=80, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField('started')
    end_time = models.DateTimeField('finished', null=True)
    total_points = models.IntegerField(default=0)
    error_points = models.IntegerField(default=0)
    ok_points = models.IntegerField(default=0)
    progress = models.IntegerField(default=0)

    reference_configuration = models.ForeignKey(to=DatasetConfiguration, on_delete=models.SET_NULL, related_name='ref_validation_run', null=True)
    ref_dataset_name = models.CharField(max_length=30, blank=True)

    scaling_ref = models.ForeignKey(to=DatasetConfiguration, on_delete=models.SET_NULL, related_name='scaling_ref_validation_run', null=True)
    scaling_method = models.CharField(max_length=20, choices=SCALING_METHODS, default=MEAN_STD)
    interval_from = models.DateTimeField(null=True)
    interval_to = models.DateTimeField(null=True)
    anomalies = models.CharField(max_length=20, choices=ANOMALIES_METHODS, default=NO_ANOM)
    min_lat = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    min_lon = models.FloatField(null=True, blank=True)
    max_lat = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    max_lon = models.FloatField(null=True, blank=True)
    # only applicable if anomalies with climatology is selected
    anomalies_from = models.DateTimeField(null=True, blank=True)
    anomalies_to = models.DateTimeField(null=True, blank=True)

    output_file = models.FileField(null=True, max_length=250, blank=True)

    is_archived = models.BooleanField(default=False)
    last_extended = models.DateTimeField(null=True, blank=True)
    expiry_notified = models.BooleanField(default=False)

    doi = models.CharField(max_length=255, blank=True)
    publishing_in_progress = models.BooleanField(default=False)

    tcol = models.BooleanField(default=False)

    # many-to-one relationships coming from other models:
    # dataset_configurations from DatasetConfiguration
    # celery_tasks from CeleryTask

    @property
    def expiry_date(self):
        if (self.is_archived or (self.end_time is None)):
            return None

        initial_date = self.last_extended if self.last_extended else self.end_time
        return initial_date + timedelta(days=settings.VALIDATION_EXPIRY_DAYS)

    @property
    def is_expired(self):
        e = self.expiry_date
        return ((e is not None) and (timezone.now() > e))

    @property
    def is_near_expiry(self):
        e = self.expiry_date
        return ((e is not None) and (timezone.now() > e - timedelta(days=settings.VALIDATION_EXPIRY_WARNING_DAYS)))

    @property
    def is_unpublished(self):
        return not self.doi

    def archive(self, unarchive=False, commit=True):
        if unarchive:
            self.extend_lifespan(commit=False)
            self.is_archived = False
        else:
            self.is_archived = True

        if commit:
            self.save()

    def extend_lifespan(self, commit=True):
        self.last_extended = timezone.now()
        self.expiry_notified = False;

        if commit:
            self.save()

    def clean(self):
        super(ValidationRun, self).clean()

        if self.interval_from is None and self.interval_to is not None:
            raise ValidationError({'interval_from': 'What has an end must have a beginning.',})
        if self.interval_from is not None and self.interval_to is None:
            raise ValidationError({'interval_to': 'What has a beginning must have an end.',})
        if self.interval_from is not None and self.interval_to is not None and self.interval_from > self.interval_to:
            raise ValidationError({'interval_from': 'From must be before To',
                                   'interval_to': 'From must be before To',})

        if self.anomalies == self.CLIMATOLOGY:
            if self.anomalies_from is None or self.anomalies_to is None:
                raise ValidationError({'anomalies': 'Need valid time period to calculate climatology from.',})
            if self.anomalies_from > self.anomalies_to:
                raise ValidationError({'anomalies_from': 'Start of climatology period must be before end.',
                                       'anomalies_to': 'Start of climatology period must be before end.',})
        else:
            if self.anomalies_from is not None or self.anomalies_to is not None:
                raise ValidationError({'anomalies': 'Time period makes no sense for anomalies calculation without climatology.',})

        box = {'min_lat': self.min_lat, 'min_lon': self.min_lon, 'max_lat': self.max_lat, 'max_lon': self.max_lon}
        if (any(x is None for x in box.values()) and any(x is not None for x in box.values())):
            affected_fields = {}
            for key, value in box.items():
                if value is None:
                    affected_fields[key] = 'For spatial subsetting, please set all bounding box coordinates.'
            raise ValidationError(affected_fields)

    def __str__(self):
        return "id: {}, user: {}, start: {} )".format(self.id, self.user, self.start_time)

    def output_dir_url(self):
        if bool(self.output_file) is False:
            return None
        url = regex_sub('[^/]+$', '', self.output_file.url)
        return url


# delete model output directory on disk when model is deleted
@receiver(post_delete, sender=ValidationRun)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.output_file:
        rundir = path.dirname(instance.output_file.path)
        if path.isdir(rundir):
            rmtree(rundir)
