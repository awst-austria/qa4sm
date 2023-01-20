from django.contrib.admin.options import ModelAdmin


class DatasetVersionAdmin(ModelAdmin):
    list_display = ('id', 'short_name', 'dataset')

    def dataset(self, obj):
        if len(obj.versions.all()):
            return obj.versions.all()[0]
        else:
            return "No dataset assigned"