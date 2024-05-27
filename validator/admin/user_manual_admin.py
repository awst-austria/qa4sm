from django.contrib.admin.options import ModelAdmin


class UserManualAdmin(ModelAdmin):
    list_display = ('id', 'file', 'upload_date')