from django.contrib.admin.options import ModelAdmin


class DatasetAdmin(ModelAdmin):
    list_display = ('id', 'short_name', 'user')
