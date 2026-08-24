from django.db import models

from validator.models.filter import DataFilter
from validator.models.dataset import Dataset
from validator.models.variable import DataVariable
from validator.models.version import DatasetVersion


class DatasetConfiguration(models.Model):
    id = models.AutoField(primary_key=True)
    # validator.models.validation_run.ValidationRun
    validation = models.ForeignKey(to='ValidationRun', on_delete=models.CASCADE, related_name='dataset_configurations', null=False)
    dataset = models.ForeignKey(to=Dataset, on_delete=models.PROTECT, related_name='dataset_configurations', null=False)
    version = models.ForeignKey(to=DatasetVersion, on_delete=models.PROTECT, related_name='dataset_configurations', null=False)
    variable = models.ForeignKey(to=DataVariable, on_delete=models.PROTECT, related_name='dataset_configurations', null=False)
    filters = models.ManyToManyField(DataFilter, related_name='dataset_configurations', blank=True)
    parametrised_filters = models.ManyToManyField(DataFilter, through='ParametrisedFilter', blank=True)
    is_spatial_reference = models.BooleanField(null=True)
    is_temporal_reference = models.BooleanField(null=True)
    is_scaling_reference = models.BooleanField(null=True)

    # depth layers of this dataset to fold into a single series on reading.
    # Fewer than two entries means no merging at all, so every pre-existing
    # configuration keeps behaving exactly as before.
    merged_variables = models.ManyToManyField(DataVariable, blank=True,
                                              related_name='merged_in_configs')
    # False gives an equal-weight mean instead of weighting each layer by how
    # much of the merged range it covers
    merge_weighted = models.BooleanField(default=True)

    @property
    def merged_layers(self):
        """
        The depth layers this configuration actually merges, shallowest first.

        Empty unless there are at least two, and both gates pass: the dataset
        must be whitelisted and every variable must be a disjoint layer. Gating
        here rather than at the call sites means a configuration that somehow
        stored an ineligible selection degrades to no merging instead of
        producing a wrong series.
        """
        from validator.validation.depths import sort_by_depth

        if not self.dataset.supports_layer_merging:
            return []

        selected = list(self.merged_variables.all())
        if len(selected) < 2:
            return []
        if not all(v.is_mergeable_layer for v in selected):
            return []

        return sort_by_depth(selected)

    @property
    def is_merged(self):
        """Whether this configuration folds several depth layers into one."""
        return bool(self.merged_layers)

    def __str__(self):
        return "Data set: {}, version: {}, variable: {}".format(
            self.dataset if hasattr(self, 'dataset') else "none",
            self.version if hasattr(self, 'version') else "none",
            self.variable if hasattr(self, 'variable') else "none",
            )

    class Meta:
        # https://docs.djangoproject.com/en/2.2/ref/models/options/#order-with-respect-to
        order_with_respect_to = 'validation'