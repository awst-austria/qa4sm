from django.contrib.admin.options import ModelAdmin
from validator.validation.globals import USER_DATASET_MIN_ID


class DatasetAdmin(ModelAdmin):
    list_display = ('id', 'short_name', 'user', 'file')

    def file(self, obj):
        if len(obj.user_dataset.all()) and obj.id >= USER_DATASET_MIN_ID:
            return obj.user_dataset.all()[0]
        elif not len(obj.user_dataset.all()) and obj.user is not None:
            return "Private admin data"
        elif obj.id < USER_DATASET_MIN_ID:
            return "Application data"
        else:
            return "No file assigned"
