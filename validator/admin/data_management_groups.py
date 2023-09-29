from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple, RelatedFieldWidgetWrapper
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from validator.models import DataManagementGroup, UserDatasetFile, User, Dataset
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Permission, ContentType
from django.contrib import messages
from django.contrib.admin.actions import delete_selected as delete_selected_


def delete_selected(modeladmin, request, queryset):
    # this method overrides delete_selected to remove confirmation message which shows up even if there is an error
    if request.POST.get('post'):
        try:
            for obj in queryset:
                obj.delete()
        except ProtectedError:
            messages.error(request, "Cannot delete some of the selected groups due to existing relationships.")
    else:
        return delete_selected_(modeladmin, request, queryset)


class DataManagementGroupForm(forms.ModelForm):
    user_datasets = forms.ModelMultipleChoiceField(
        queryset=Dataset.objects.all(),
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
    actions = [delete_selected]
    form = DataManagementGroupForm
    list_display = ('name', 'group_owner', 'permission_list', 'users', 'user_datasets')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        content_type_id = ContentType.objects.get_for_model(DataManagementGroup)
        form.base_fields['group_owner'].queryset = User.objects.filter(id=request.user.id)
        form.base_fields['permissions'].queryset = Permission.objects.filter(content_type_id=content_type_id)
        form.base_fields['user_datasets'].queryset = Dataset.objects.filter(user=request.user)
        form.base_fields['users'].queryset = User.objects.exclude(id=request.user.id)

        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        shared_datasets = form.cleaned_data['user_datasets']
        used_datasets = obj.get_list_of_group_ds_used_by_group_users()

        group_users = form.cleaned_data['users']
        users_using_datasets = obj.get_list_of_group_users_using_group_ds()

        trying_to_remove_used_ds = used_datasets and not used_datasets.intersection(shared_datasets).exists()
        trying_to_remove_user_using_ds = users_using_datasets and not users_using_datasets.intersection(
            group_users).exists()

        if trying_to_remove_used_ds or trying_to_remove_user_using_ds:
            messages.error(request,
                           "Changes can not be saved. "
                           "At least one of the users uses the dataset shared within the group.")
        else:
            obj.custom_datasets.set(shared_datasets)
            obj.user_set.set(group_users)

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

    def response_change(self, request, obj):
        if request.method == 'POST' and hasattr(request, '_messages'):
            if any(message.level == messages.ERROR for message in request._messages):
                messages.error(request,
                               "Changes can not be saved. At least one of the users uses the dataset shared within "
                               "the group.")
                return redirect(request.path)
        return super().response_change(request, obj)

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
