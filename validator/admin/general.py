from django.contrib import admin
from django.contrib.auth import get_user_model
User = get_user_model()

from validator.admin import CustomUserAdmin
from validator.admin import SystemSettingsAdmin
from validator.admin import ValidationRunAdmin
from validator.models import DataFilter
from validator.models import DataVariable
from validator.models import Dataset
from validator.models import DatasetVersion
from validator.models import Settings
from validator.models import ValidationRun


admin.site.register(Settings, SystemSettingsAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ValidationRun, ValidationRunAdmin)
admin.site.register(DataFilter)
admin.site.register(Dataset)
admin.site.register(DatasetVersion)
admin.site.register(DataVariable)
