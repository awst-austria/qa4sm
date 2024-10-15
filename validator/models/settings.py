from django.db import models

class Settings(models.Model):
    class Meta:
        verbose_name_plural = "Settings"

    id = models.AutoField(primary_key=True)
    maintenance_mode = models.BooleanField(default=True)
    potential_maintenance = models.BooleanField(default=False)
    news = models.TextField(blank=True)
    potential_maintenance_description = models.TextField(blank=True)
    sum_link = models.CharField(max_length=250, blank=True, verbose_name='User Manual Link')
    feed_link = models.CharField(max_length=250, blank=True, verbose_name='Feedback Link')

    def save(self, *args, **kwargs):
        self.pk = 1
        super(Settings, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'maintenance mode: {}, news: {}'.format(self.maintenance_mode, self.news)
