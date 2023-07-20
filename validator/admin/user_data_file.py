from django.contrib.admin.options import ModelAdmin


class UserDatasetFileAdmin(ModelAdmin):
    list_display = ('id', 'file_name', 'owner', 'dataset', 'version', 'upload_date', 'file_size', 'user_groups_list')
    list_filter = ('owner', 'dataset', 'version', 'upload_date')
    ordering = ('owner', 'upload_date','dataset', 'version')

    def user_groups_list(self, obj):
        return list(obj.user_groups.all())