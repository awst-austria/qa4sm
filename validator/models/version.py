from django.db import models, transaction
from django.dispatch import receiver
from validator.models.filter import DataFilter
from django.db.models.signals import post_save
from django.apps import apps

class DatasetVersion(models.Model):
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=40)
    help_text = models.CharField(max_length=150)
    time_range_start = models.TextField(blank=True, null=True)
    time_range_end = models.TextField(blank=True, null=True)
    geographical_range = models.JSONField(blank=True, null=True)
    filters = models.ManyToManyField(DataFilter, related_name='filters', blank=True)
    usage_count = models.IntegerField(default=0)

    def __str__(self):
        return self.short_name

@receiver(post_save, sender='validator.ValidationRun')
def incrementUsage(sender, instance, created, **kwargs):
    if created:

        def update_dataset_usage():
            datasetVersion = apps.get_model('validator', 'DatasetVersion')  # Avoid circular import
            usedSets = [
                instance.spatial_reference_configuration,
                instance.temporal_reference_configuration,
                instance.scaling_ref
            ] 
        
            for config in usedSets:
                if config:
                    version = config.version
                    print([version])
                    datasetVersion.objects.filter(short_name=version).update(usage_count=models.F('usage_count') + 1)

        transaction.on_commit(update_dataset_usage)   