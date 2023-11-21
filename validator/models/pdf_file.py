from django.core.files.storage import FileSystemStorage
from django.db import models
from valentina.settings_conf import DOCS_DIR, SITE_URL
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_delete
from shutil import rmtree
from os import path
from validator.models import Settings
import uuid

key_store = FileSystemStorage(location=DOCS_DIR)


class PdfFiles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(null=True, blank=True, storage=key_store, upload_to='./files_to_serve')
    file_name = models.CharField(max_length=100, blank=True, null=True)
    upload_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.file_name == 'UserManual':
            settings = Settings.objects.all().first()
            settings.sum_link = SITE_URL + f'/api/get-pdf-file?file_id={self.id}'
            settings.save()

        super(PdfFiles, self).save(*args, **kwargs)


@receiver(post_delete, sender=PdfFiles)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        rundir = path.dirname(instance.file.path)
        if path.isdir(rundir):
            rmtree(rundir)
