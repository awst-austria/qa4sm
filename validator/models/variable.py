from django.db import models
from django.db.models import Q

class DataVariable(models.Model):
    # whether this variable is a disjoint depth layer that may take part in a
    # layer merge. Kept deliberately separate from depth_from/depth_to: the
    # depths say *what depth this is* and are filled in wherever known (including
    # on aggregates), while depth_kind says *may this be merged*. Encoding
    # "don't merge" as a missing depth would throw away a true fact and would
    # break the moment someone helpfully fills the blank in.
    class DepthKind(models.TextChoices):
        LAYER = 'layer', 'Disjoint depth layer'
        AGGREGATE = 'aggregate', 'Pre-averaged over a depth span'
        NA = '', 'Depth not applicable'

    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, default='n.a.')
    help_text = models.CharField(max_length=150)

    min_value = models.FloatField(null=True)
    max_value = models.FloatField(null=True)
    display_name = models.CharField(max_length=100, default='n.a.', blank=True)

    # depth of the soil layer this variable represents, in metres below surface
    depth_from = models.FloatField(null=True, blank=True)
    depth_to = models.FloatField(null=True, blank=True)
    depth_kind = models.CharField(max_length=10,
                                  blank=True,
                                  choices=DepthKind.choices,
                                  default=DepthKind.NA)

    # many-to-one relationships coming from other models:
    # dataset_configuration from DatasetConfiguration

    def __str__(self):
        return self.short_name

    @property
    def thickness(self):
        """Layer thickness in metres, or None if this variable has no depth."""
        if self.depth_from is None or self.depth_to is None:
            return None
        return self.depth_to - self.depth_from

    @property
    def is_mergeable_layer(self):
        """Whether this variable may take part in a depth-layer merge."""
        return (self.depth_kind == self.DepthKind.LAYER
                and self.depth_from is not None
                and self.depth_to is not None)

    class Meta:
        constraints = [
            # a declared kind must come with both bounds, so that a half-filled
            # row can never look like a valid layer
            models.CheckConstraint(
                name='depth_bounds_required_when_kind_declared',
                condition=Q(depth_kind='') | (Q(depth_from__isnull=False)
                                              & Q(depth_to__isnull=False))),
        ]
