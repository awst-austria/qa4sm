from django.contrib.admin.options import ModelAdmin


class DatasetVariableAdmin(ModelAdmin):
    list_display = ('id', 'short_name', 'version')

    def version(self, obj):
        if len(obj.variables.all()):
            return obj.variables.all()[0]
        else:
            return "No dataset assigned"