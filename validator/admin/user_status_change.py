from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()

from validator.mailer import send_user_status_changed


# "buisness logic" that changes the user status and sends mails
def user_status_change(user, activate, notify):
    # if user already has desired status, do nothing
    if user.is_active == activate:
        return user

    user.is_active = activate
    user.save()
    if notify:
        send_user_status_changed(user, activate)

    return user

# bulk activities for the action menu in the list view
def bulk_user_activation(modeladmin, request, queryset):
    for user in queryset:
        try:
            user_status_change(user, activate=True, notify=True )
        except Exception as e:
            modeladmin.message_user('Error activating user: {}'.format(e))
bulk_user_activation.short_description = "Activate (and notify) selected users"
bulk_user_activation.allowed_permissions = ('change',)

def bulk_user_deactivation(modeladmin, request, queryset):
    for user in queryset:
        try:
            user_status_change(user, activate=False, notify=True )
        except Exception as e:
            modeladmin.message_user('Error deactivating user: {}'.format(e))
bulk_user_deactivation.short_description = "Deactivate (and notify) selected users"
bulk_user_deactivation.allowed_permissions = ('change',)

def silent_bulk_user_activation(modeladmin, request, queryset):
    for user in queryset:
        try:
            user_status_change(user, activate=True, notify=False )
        except Exception as e:
            modeladmin.message_user('Error activating user: {}'.format(e))
silent_bulk_user_activation.short_description = "Silently activate selected users"
silent_bulk_user_activation.allowed_permissions = ('change',)

def silent_bulk_user_deactivation(modeladmin, request, queryset):
    for user in queryset:
        try:
            user_status_change(user, activate=False, notify=False )
        except Exception as e:
            modeladmin.message_user('Error activating user: {}'.format(e))
silent_bulk_user_deactivation.short_description = "Silently deactivate selected users"
silent_bulk_user_deactivation.allowed_permissions = ('change',)


# form for changing the user status (activate/deactivate)
class UserStatusChangeForm(forms.Form):
    DEACTIVATE = 'deactivate'
    ACTIVATE = 'activate'

    STATUS_ITEMS = {
        DEACTIVATE: (DEACTIVATE,'deactivate their account'),
        ACTIVATE: (ACTIVATE,'activate their account'),
        }
    STATUS_ACTIONS = STATUS_ITEMS.values()

    status_action = forms.ChoiceField(choices=STATUS_ACTIONS, widget=forms.RadioSelect(), label='')
    send_email = forms.BooleanField(required=False, initial=True, label='Send them a notification')

    def save(self, user):
        notify = self.cleaned_data.get('send_email', True)
        s_action = self.cleaned_data.get('status_action', self.DEACTIVATE)
        activate = (s_action == self.ACTIVATE)

        try:
            user = user_status_change(user, activate, notify)
        except Exception as e:
            error_message = str(e)
            self.add_error(None, error_message)
            raise

        return user
