from django.contrib.admin import ModelAdmin


class DatasetConfigurationAdmin(ModelAdmin):
    list_display = ['id', 'validation_id', 'dataset', 'version']
    ordering = ['validation_id']