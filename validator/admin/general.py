from django.contrib import admin
from django.contrib.auth import get_user_model
from validator.admin import CustomUserAdmin
from validator.admin import SystemSettingsAdmin
from validator.admin import ValidationRunAdmin
from validator.admin import StatisticsAdmin
from validator.admin import EmailAdmin
from validator.admin import UptimeMonitoringAdmin
from validator.admin import UserDatasetFileAdmin
from validator.admin import DatasetAdmin
from validator.admin import DatasetVersionAdmin
from validator.admin import DatasetVariableAdmin
from validator.admin.data_management_groups import DataManagementGroupAdmin
from validator.admin.pdf_file_admin import PdfFileAdmin
from validator.models import DataFilter
from validator.models import DataVariable
from validator.models import Dataset
from validator.models import DatasetVersion
from validator.models import Settings
from validator.models import ValidationRun
from validator.models import Statistics
from validator.models import Email
from validator.models import UptimeReport
from validator.models import UserDatasetFile
from validator.models import DataManagementGroup
from validator.models import PdfFiles
User = get_user_model()

admin.site.register(Settings, SystemSettingsAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ValidationRun, ValidationRunAdmin)
admin.site.register(DataFilter)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DatasetVersion, DatasetVersionAdmin)
admin.site.register(DataVariable, DatasetVariableAdmin)
admin.site.register(Statistics, StatisticsAdmin)
admin.site.register(Email, EmailAdmin)
admin.site.register(UptimeReport, UptimeMonitoringAdmin)
admin.site.register(UserDatasetFile, UserDatasetFileAdmin)
admin.site.register(DataManagementGroup, DataManagementGroupAdmin)
admin.site.register(PdfFiles, PdfFileAdmin)
