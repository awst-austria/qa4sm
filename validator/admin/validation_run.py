from django.conf import settings
from django.utils.html import format_html
from django.contrib.admin.options import ModelAdmin, TabularInline

from api.frontend_urls import get_angular_url
from validator.models.dataset_configuration import DatasetConfiguration


# see https://docs.djangoproject.com/en/2.1/ref/contrib/admin/#inlinemodeladmin-objects
class DatasetConfigurationInline(TabularInline):
    model = DatasetConfiguration
    fk_name = "validation"
    extra = 0


# for tutorial see https://djangobook.com/customizing-change-lists-forms/
class ValidationRunAdmin(ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'user', 'name_tag', 'open_button',  'is_expired', 'expiry_notified', 'isRemoved')
    readonly_fields = (
        'spatial_reference_configuration', 'temporal_reference_configuration',
        'scaling_ref',)
    search_fields = ('name_tag',)
    list_filter = ('start_time', 'end_time', 'user')
    ordering = ('-start_time', '-end_time',)

    inlines = [DatasetConfigurationInline, ]

    def __init__(self, model, admin_site):
        super(ValidationRunAdmin, self).__init__(model, admin_site)

    ## return 'open' button
    def open_button(self, valrun):
        return format_html(
            '<a class="button" target="_blank" href="{}">Open</a>',
            settings.SITE_URL + get_angular_url('result', valrun.id),
        )

    open_button.short_description = 'Open'
    open_button.allow_tags = True
