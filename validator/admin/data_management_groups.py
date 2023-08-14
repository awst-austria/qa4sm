from django import forms
from django.contrib.admin import ModelAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple

from validator.models import DataManagementGroup, UserDatasetFile, User
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Permission, ContentType


class DataManagementGroupForm(forms.ModelForm):
    user_datasets = forms.ModelMultipleChoiceField(
        queryset=UserDatasetFile.objects.all(),
        widget=FilteredSelectMultiple('User Datasets', False),
        required=False
    )
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=FilteredSelectMultiple('Users', False),
        required=False
    )

    class Meta:
        model = DataManagementGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['user_datasets'].initial = self.instance.custom_datasets.all()
            self.fields['users'].initial = self.instance.user_set.all()


class DataManagementGroupAdmin(GroupAdmin, ModelAdmin):
    form = DataManagementGroupForm
    list_display = ('name', 'group_owner', 'permission_list', 'users', 'user_datasets')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        content_type_id = ContentType.objects.get_for_model(DataManagementGroup)
        form.base_fields['group_owner'].queryset = User.objects.filter(id=request.user.id)
        form.base_fields['permissions'].queryset = Permission.objects.filter(content_type_id=content_type_id)
        form.base_fields['user_datasets'].queryset = UserDatasetFile.objects.filter(owner=request.user)
        form.base_fields['users'].queryset = User.objects.exclude(id=request.user.id)

        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        obj.custom_datasets.set(form.cleaned_data['user_datasets'])
        obj.user_set.set(form.cleaned_data['users'])

    @staticmethod
    def permission_list(obj):
        perms = obj.permissions.all()
        return list(perms.values_list('name', flat=True))

    @staticmethod
    def user_datasets(obj):
        return list(obj.custom_datasets.all())

    @staticmethod
    def users(obj):
        return list(obj.user_set.all())
