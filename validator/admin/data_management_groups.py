from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple, RelatedFieldWidgetWrapper
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from validator.models import DataManagementGroup, UserDatasetFile, User
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Permission, ContentType
from django.contrib import messages
from django.contrib.admin.actions import delete_selected


def custom_delete_selected(modeladmin, request, queryset):
    # this method overrides delete_selected to remove confirmation message which shows up even if there is an error
    if request.POST.get('post'):
        try:
            for obj in queryset:
                obj.delete()
        except ProtectedError:
            messages.error(request, "Cannot delete some of the selected groups due to existing relationships.")
    else:
        return delete_selected(modeladmin, request, queryset)


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
            print(self.instance.get_list_of_group_ds_used_by_group_users())


class DataManagementGroupAdmin(GroupAdmin, ModelAdmin):
    actions = [custom_delete_selected]
    form = DataManagementGroupForm
    list_display = ('name', 'group_owner', 'permission_list', 'users', 'user_datasets')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        content_type_id = ContentType.objects.get_for_model(DataManagementGroup)
        form.base_fields['group_owner'].queryset = User.objects.filter(id=request.user.id)
        form.base_fields['permissions'].queryset = Permission.objects.filter(content_type_id=content_type_id)
        form.base_fields['user_datasets'].queryset = UserDatasetFile.objects.filter(owner=request.user)

        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # obj.group_owner = request.user
        obj.custom_datasets.set(form.cleaned_data['user_datasets'])
        obj.user_set.set(form.cleaned_data['users'])

    def delete_view(self, request, object_id, extra_context=None):
        model = self.model
        obj = self.get_object(request, object_id)

        try:
            self.log_deletion(request, obj, obj.__str__())
            obj.delete()
            return self.response_delete(request, obj_display=obj.__str__(), obj_id=obj.id)
        except ProtectedError:
            messages.error(request, "Cannot delete the model instance due to existing relationships.")
            return redirect(f'admin:{model._meta.app_label}_{model._meta.model_name}_change', object_id)

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
