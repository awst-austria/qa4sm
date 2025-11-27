import os
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

from validator.models import DatasetConfiguration, User, CopiedValidations, Dataset
from django.db.models import Q, ExpressionWrapper, F, BooleanField

from validator.models.validation_run_deleted import DeletedValidationRun

# def get_spatial_reference_id(instance) -> int:
#     return instance.spatial_reference_configuration.primary_key

DATASETS_WITHOUT_FILES = []


class ValidationRun(models.Model):
    # scaling methods
    MIN_MAX = 'min_max'
    LINREG = 'linreg'
    MEAN_STD = 'mean_std'
    NO_SCALING = 'none'
    BETA_SCALING = 'cdf_beta_match'

    SCALING_METHODS = (
        (NO_SCALING, 'No scaling'),
        (MIN_MAX, 'Min/Max'),
        (LINREG, 'Linear regression'),
        (MEAN_STD, 'Mean/standard deviation'),
        (BETA_SCALING, 'CDF matching with beta distribution fitting'),
    )

    # scale to
    SCALE_TO_REF = 'ref'
    SCALE_TO_DATA = 'data'

    SCALE_TO_OPTIONS = (
        (SCALE_TO_REF, 'Scale to reference'),
        (SCALE_TO_DATA, 'Scale to data')
    )

    # anomalies
    MOVING_AVG_35_D = "moving_avg_35_d"
    CLIMATOLOGY = "climatology"
    NO_ANOM = "none"
    ANOMALIES_METHODS = (
        (NO_ANOM, 'Do not calculate'),
        (MOVING_AVG_35_D, '35 day moving average'),
        (CLIMATOLOGY, 'Climatology'),
    )

    # upscaling options
    NO_UPSCALE = "none"
    AVERAGE = "average"
    UPSCALING_METHODS = (
        (NO_UPSCALE, 'Do not upscale point measurements'),
        (AVERAGE, 'Average point measurements'),
    )

    # temporal matching window size:
    TEMP_MATCH_WINDOW = 12

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('RUNNING', 'Running'),
        ('DONE', 'Done'),
        ('CANCELLED', 'Cancelled'),
        ('ERROR', 'Error'),
    ]
    # fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_tag = models.CharField(max_length=80, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField('started')
    end_time = models.DateTimeField('finished', null=True)
    total_points = models.IntegerField(default=0)
    error_points = models.IntegerField(default=0)
    ok_points = models.IntegerField(default=0)
    progress = models.IntegerField(default=0)

    spatial_reference_configuration = models.ForeignKey(to=DatasetConfiguration, on_delete=models.SET_NULL,
                                                        related_name='spat_ref_validation_run', null=True)
    temporal_reference_configuration = models.ForeignKey(to=DatasetConfiguration, on_delete=models.SET_NULL,
                                                         related_name='temp_ref_validation_run', null=True)
    scaling_ref = models.ForeignKey(to=DatasetConfiguration, on_delete=models.SET_NULL,
                                    related_name='scaling_ref_validation_run', null=True)
    scaling_method = models.CharField(max_length=20, choices=SCALING_METHODS, default=NO_SCALING)
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
    # upscaling of ISMN point measurements
    upscaling_method = models.CharField(max_length=50, choices=UPSCALING_METHODS, default=NO_UPSCALE, blank=True)
    temporal_stability = models.BooleanField(default=False)

    output_file = models.FileField(null=True, max_length=250, blank=True)
    zarr_path = models.CharField(max_length=350, null=True, blank=True)

    is_archived = models.BooleanField(default=False)
    last_extended = models.DateTimeField(null=True, blank=True)
    expiry_notified = models.BooleanField(default=False)

    doi = models.CharField(max_length=255, blank=True)
    publishing_in_progress = models.BooleanField(default=False)

    tcol = models.BooleanField(default=False)
    bootstrap_tcol_cis = models.BooleanField(default=False)
    used_by = models.ManyToManyField(User, through=CopiedValidations, through_fields=('original_run', 'used_by_user'),
                                     related_name='copied_runs')
    temporal_matching = models.IntegerField(default=TEMP_MATCH_WINDOW, null=False, blank=False,
                                            validators=[MinValueValidator(1), MaxValueValidator(24)])

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SCHEDULED')

    # many-to-one relationships coming from other models:
    # dataset_configurations from DatasetConfiguration
    # celery_tasks from CeleryTask

    @property
    def expiry_date(self):
        if (self.is_archived or (self.end_time is None)) and (self.progress != -1):
            return None

        if self.progress == -1:
            initial_date = self.start_time
        else:
            initial_date = self.last_extended if self.last_extended else self.end_time

        return initial_date + timedelta(days=settings.VALIDATION_EXPIRY_DAYS)

    @property
    def is_expired(self):
        e = self.expiry_date
        return (e is not None) and (timezone.now() > e)

    @property
    def is_near_expiry(self):
        e = self.expiry_date
        return (e is not None) and (timezone.now() > e - timedelta(days=settings.VALIDATION_EXPIRY_WARNING_DAYS))

    @property
    def is_unpublished(self):
        return not self.doi


    @property
    def all_files_exist(self):
        return len(self.get_dataset_configs_without_file()) == 0

    def get_graphics_path(self):
        return self.output_file.path.replace(self.output_file.name, f'{self.id}/graphs.zip')

    def get_dataset_configs_without_file(self):
        return self.dataset_configurations.all().filter(dataset__storage_path='')

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
        self.expiry_notified = False

        if commit:
            self.save()

    def clean(self):
        super(ValidationRun, self).clean()

        if self.interval_from is None and self.interval_to is not None:
            raise ValidationError({'interval_from': 'What has an end must have a beginning.', })
        if self.interval_from is not None and self.interval_to is None:
            raise ValidationError({'interval_to': 'What has a beginning must have an end.', })
        if self.interval_from is not None and self.interval_to is not None and self.interval_from > self.interval_to:
            raise ValidationError({'interval_from': 'From must be before To',
                                   'interval_to': 'From must be before To', })

        if self.anomalies == self.CLIMATOLOGY:
            if self.anomalies_from is None or self.anomalies_to is None:
                raise ValidationError({'anomalies': 'Need valid time period to calculate climatology from.', })
            if self.anomalies_from > self.anomalies_to:
                raise ValidationError({'anomalies_from': 'Start of climatology period must be before end.',
                                       'anomalies_to': 'Start of climatology period must be before end.', })
        else:
            if self.anomalies_from is not None or self.anomalies_to is not None:
                raise ValidationError(
                    {'anomalies': 'Time period makes no sense for anomalies calculation without climatology.', })

        box = {'min_lat': self.min_lat, 'min_lon': self.min_lon, 'max_lat': self.max_lat, 'max_lon': self.max_lon}
        if any(x is None for x in box.values()) and any(x is not None for x in box.values()):
            affected_fields = {}
            for key, value in box.items():
                if value is None:
                    affected_fields[key] = 'For spatial subsetting, please set all bounding box coordinates.'
            raise ValidationError(affected_fields)

    def __str__(self):
        return "id: {}, user: {}, start: {} )".format(self.id, self.user, self.start_time)

    @property
    def output_dir_url(self):
        if bool(self.output_file) is False:
            return None
        url = regex_sub('[^/]+$', '', self.output_file.url)
        return url

    @property
    def output_file_name(self):
        if bool(self.output_file) is False:
            return None
        name = self.output_file.name.split('/')[1]
        return name

    @property
    def is_a_copy(self):
        copied_runs = CopiedValidations.objects.filter(copied_run_id=self.id) \
            .annotate(is_copied=ExpressionWrapper(~Q(copied_run=F('original_run')), output_field=BooleanField())) \
            .filter(is_copied=True)

        return len(copied_runs) != 0

    @property
    def comparison_label(self):
        # check name tag has been given and it's not empty
        if self.name_tag is not None and self.name_tag:
            return self.name_tag

        configs = DatasetConfiguration.objects.filter(validation=self.id)
        datasets = [conf.dataset.short_name + ', ' for conf in configs if
                    conf.id != self.spatial_reference_configuration.id]

        label = f"Validation date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}, Non-reference-dataset: "
        for dataset in datasets:
            label += dataset
        label = label.strip(', ')

        return label

    def user_data_panel_label(self):
        if self.name_tag is not None and self.name_tag:
            return self.name_tag
        config = DatasetConfiguration.objects.filter(validation=self.id).get(is_spatial_reference=True)
        label = f"Date: {self.start_time.strftime('%Y-%m-%d')}, Spatial-reference: " \
                f"{config.dataset.short_name}"
        return label

    @property
    def contains_user_data(self):
        user_data = [conf for conf in self.dataset_configurations.all() if conf.dataset.user_dataset.all()]
        return len(user_data) > 0

    def update_status(self):
        from validator.validation.util import determine_status  # Delayed Import to avoid circular imports
        self.status = determine_status(self.progress, self.end_time, self.status)

    def save(self, *args, **kwargs):
        """Override save to automatically update status."""
        self.update_status()
        super().save(*args, **kwargs)


    def delete(self, using=None, keep_parents=False):
        global DATASETS_WITHOUT_FILES
        DATASETS_WITHOUT_FILES = list(self.get_dataset_configs_without_file().values_list('dataset', flat=True))
        create_deleted_validation_run(self)
        super().delete(using=using, keep_parents=keep_parents)

    # delete model output directory on disk when model is deleted


@receiver(post_delete, sender=ValidationRun)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    # I know external modules should be imported at the very beginning of the file, but in this case it doesn't work,
    # I haven't found a solution for that, so I import it here
    from validator.validation.globals import OUTPUT_FOLDER

    # here I need to check if there are datasets assigned to this validation that do not have files and if they're not
    # use anywhere else, the dataset can be removed

    if len(DATASETS_WITHOUT_FILES) > 0:
        datasets_to_delete = Dataset.objects.filter(
            id__in=DATASETS_WITHOUT_FILES,
            dataset_configurations__isnull=True
        )
        for dataset in datasets_to_delete:
            dataset.user_dataset.first().delete()

    if instance.output_file:
        rundir = path.dirname(instance.output_file.path)
        if path.isdir(rundir):
            rmtree(rundir)
    else:
        # this part has to be added, otherwise, when a validation is canceled an empty directory remains
        outdir = os.path.join(OUTPUT_FOLDER, str(instance.id))
        if os.path.isdir(outdir):
            rmtree(outdir)


def create_deleted_validation_run(instance):
    val_datasets = [f'{config.dataset.pretty_name}/{config.version.pretty_name}/{config.variable.pretty_name}' for config in instance.dataset_configurations.all()]
    spatial_ref_config = instance.spatial_reference_configuration
    temporal_ref_config = instance.temporal_reference_configuration
    scaling_ref_config = instance.scaling_ref
    scaling_ref = None if not scaling_ref_config else \
        f'{scaling_ref_config.dataset.pretty_name}/{scaling_ref_config.version.pretty_name}/{scaling_ref_config.variable.pretty_name}'
    spatial_ref = None if not spatial_ref_config else \
        f'{spatial_ref_config.dataset.pretty_name}/{spatial_ref_config.version.pretty_name}/{spatial_ref_config.variable.pretty_name}'
    temporal_ref = None if not temporal_ref_config else \
        f'{temporal_ref_config.dataset.pretty_name}/{temporal_ref_config.version.pretty_name}/{temporal_ref_config.variable.pretty_name}'

    DeletedValidationRun.objects.create(
        id=instance.id,
        user=instance.user,
        start_time=instance.start_time,
        end_time=instance.end_time,
        total_points=instance.total_points,
        error_points=instance.error_points,
        ok_points=instance.ok_points,
        datasets=val_datasets,
        spatial_reference=spatial_ref,
        temporal_reference=temporal_ref,
        scaling_reference=scaling_ref,
        scaling_method=instance.scaling_method,
        interval_from=instance.interval_from,
        interval_to=instance.interval_to,
        anomalies=instance.anomalies,
        min_lat=instance.min_lat,
        min_lon=instance.min_lon,
        max_lat=instance.max_lat,
        max_lon=instance.max_lon,
        anomalies_from=instance.anomalies_from,
        anomalies_to=instance.anomalies_to,
        upscaling_method=instance.upscaling_method,
        temporal_stability=instance.temporal_stability,
        tcol=instance.tcol,
        bootstrap_tcol_cis=instance.bootstrap_tcol_cis,
        temporal_matching=instance.temporal_matching,
        plots_save_metadata=instance.plots_save_metadata,
        intra_annual_metrics=instance.intra_annual_metrics,
        intra_annual_type=instance.intra_annual_type,
        intra_annual_overlap=instance.intra_annual_overlap,
        stability_metrics=instance.stability_metrics,
        status=instance.status
    )