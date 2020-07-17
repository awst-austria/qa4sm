from django.db import models

class Settings(models.Model):
    class Meta:
        verbose_name_plural = "Settings"

    maintenance_mode = models.BooleanField(default=True)
    news = models.TextField(blank=True)

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
