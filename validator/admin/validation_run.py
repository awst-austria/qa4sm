from django.contrib.admin import ModelAdmin
from django.utils.html import format_html
from django.urls.base import reverse

# for tutorial see https://djangobook.com/customizing-change-lists-forms/
class ValidationRunAdmin(ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'user', 'name_tag', 'data_dataset', 'ref_dataset', 'open_button', )
    search_fields = ('name_tag', )
    list_filter = ('start_time', 'end_time', 'user', 'data_dataset', 'ref_dataset')
    ordering = ('-start_time', '-end_time',)

    def __init__(self, model, admin_site):
        super(ValidationRunAdmin, self).__init__(model, admin_site)

    ## return 'open' button
    def open_button(self, valrun):
        return format_html(
            '<a class="button" target="_blank" href="{}">Open</a>',
            reverse('result', args=[valrun.id]),
        )
    open_button.short_description = 'Open'
    open_button.allow_tags = True
