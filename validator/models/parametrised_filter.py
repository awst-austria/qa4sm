from django.core.exceptions import ValidationError
from django.db import models

from validator.models import DataFilter
from validator.models.dataset_configuration import DatasetConfiguration


class ParametrisedFilter(models.Model):
    id = models.AutoField(primary_key=True)
    dataset_config = models.ForeignKey(to=DatasetConfiguration, on_delete=models.CASCADE, null=False)
    filter = models.ForeignKey(to=DataFilter, on_delete=models.PROTECT, null=False)
    parameters = models.TextField()

    def __str__(self):
        return "Filter: {}; parameters: {}".format(
            self.filter if hasattr(self, 'filter') else "none",
            self.parameters if hasattr(self, 'parameters') else "none",
            )

    def clean(self):
        super(ParametrisedFilter, self).clean()
        if not self.filter.parameterised:
            raise ValidationError({'filter': 'Can\'t parametrise this filter.',})
