from django.contrib.admin.options import ModelAdmin


class UserDatasetFileAdmin(ModelAdmin):
    list_display = ('id', 'file_name', 'owner', 'dataset', 'version', 'variable', 'upload_date')
    list_filter = ('owner', 'dataset', 'version', 'upload_date')
    ordering = ('owner', 'upload_date','dataset', 'version')