from django.core.files.storage import FileSystemStorage
from django.db import models
from valentina.settings_conf import DOCS_DIR
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_delete
from shutil import rmtree
from os import path
import uuid

key_store = FileSystemStorage(location=DOCS_DIR)


class UserManual(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(null=True, blank=True, storage=key_store, upload_to='./user_manual')
    upload_date = models.DateTimeField()


@receiver(post_delete, sender=UserManual)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        rundir = path.dirname(instance.file.path)
        if path.isdir(rundir):
            rmtree(rundir)
