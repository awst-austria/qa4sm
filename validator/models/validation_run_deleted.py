import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class DeletedValidationRun(models.Model):
    # fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField('started')
    end_time = models.DateTimeField('finished', null=True)
    total_points = models.IntegerField(default=0)
    error_points = models.IntegerField(default=0)
    ok_points = models.IntegerField(default=0)
    datasets = models.JSONField(default=list)
    spatial_reference = models.CharField(max_length=200, default=None, null=True)
    temporal_reference = models.CharField(max_length=200, default=None, null=True)
    scaling_reference = models.CharField(max_length=200, default=None, null=True)
    scaling_method = models.CharField(max_length=20, default=None)
    interval_from = models.DateTimeField(null=True)
    interval_to = models.DateTimeField(null=True)
    anomalies = models.CharField(max_length=20, default=None)
    min_lat = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    min_lon = models.FloatField(null=True, blank=True)
    max_lat = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    max_lon = models.FloatField(null=True, blank=True)
    # only applicable if anomalies with climatology is selected
    anomalies_from = models.DateTimeField(null=True, blank=True)
    anomalies_to = models.DateTimeField(null=True, blank=True)
    # upscaling of ISMN point measurements
    upscaling_method = models.CharField(max_length=50,  blank=True)
    temporal_stability = models.BooleanField(default=False)

    tcol = models.BooleanField(default=False)
    bootstrap_tcol_cis = models.BooleanField(default=False)
    temporal_matching = models.IntegerField(default=None, null=False, blank=True)

    plots_save_metadata = models.CharField(
        max_length=10,
        choices=(
            ('always', 'force creating metadata box plots (e.g. for testing)'),
            ('never', 'do not create metadata box plots at all'),
            ('threshold', 'create metadata box plots only when the minimum '
                          'number of required points is available '
                          '(set in globals of qa4sm-reader'),
        ),
        default='threshold'
    )
    intra_annual_metrics = models.BooleanField(default=False)
    intra_annual_type = models.CharField(max_length=100, blank=True, null=True)
    intra_annual_overlap = models.IntegerField(blank=True, null=True)

    stability_metrics = models.BooleanField(default=False)
    status = models.CharField(max_length=10, default='DONE')


    def __str__(self):
        return "id: {}, user: {}, start: {} )".format(self.id, self.user, self.start_time)
