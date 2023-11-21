from django.contrib.admin.options import ModelAdmin


class PdfFileAdmin(ModelAdmin):
    list_display = ('id', 'file_name', 'file', 'upload_date')