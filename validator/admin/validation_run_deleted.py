from django.contrib.admin import ModelAdmin


class DeletedValidationRunAdmin(ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'user',)
    readonly_fields = (
        'spatial_reference', 'temporal_reference',
        'scaling_reference',)
    search_fields = ('datasets',)
    list_filter = ('start_time', 'end_time', 'user')
    ordering = ('-start_time', '-end_time',)
