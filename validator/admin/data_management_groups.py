from django.contrib.admin.options import ModelAdmin


class DataManagementGroupAdmin(ModelAdmin):
    list_display = ('name', 'users')

    def users(self, obj):
        return obj.user_set.all()
