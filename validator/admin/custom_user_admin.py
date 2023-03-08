from django.contrib.admin.utils import unquote
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.admin import UserAdmin, csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.urls import path
from django.urls.base import reverse
from django.utils.html import escape
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from validator.admin import bulk_send_email_to_users

from validator.admin.user_status_change import *  # @UnusedWildImport


# Customise the admin form: add more user attributes and add status change buttons
class CustomUserAdmin(UserAdmin):
    actions = [] # need to 'override' the parent actions so that we don't change all ModelAdmin actions!

    ## define which columns appear in the list view. Add the action buttons at the end.
    readonly_fields = ('user_actions', )
    list_display = ('username', 'email', 'first_name', 'last_name', 'organisation', 'orcid', 'is_active', 'is_staff', 'date_joined', 'user_actions', 'data_space')
    ordering = ('-date_joined', )

    def __init__(self, model, admin_site):
        super(CustomUserAdmin, self).__init__(model, admin_site)
        self.actions += [bulk_user_activation, bulk_user_deactivation,
                         silent_bulk_user_activation, silent_bulk_user_deactivation, bulk_send_email_to_users]
        for field_name, attributes in self.fieldsets:
            ## add the organisation field to the Personal info part of the user
            ## admin form
            if (field_name == 'Personal info' and 'fields' in attributes):
                attributes['fields'] += ('organisation', 'country', 'orcid')
#             ## add the action button(s) (change status) to the detail view
            if (field_name == 'Permissions' and 'fields' in attributes):
                attributes['fields'] = ('user_actions', ) + attributes['fields']


    ## add the url for our user status change action
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<user_id>/changestatus/',
                self.admin_site.admin_view(self.change_user_status),
                name='user_change_status'),
        ]
        return custom_urls + urls

    ## return action button(s)
    def user_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Change status</a>',
            reverse('admin:user_change_status', args=[obj.pk]),
        )
    user_actions.short_description = 'Activate / Deactivate'
    user_actions.allow_tags = True

    ## this is the view for the status change
    @csrf_protect_m
    def change_user_status(self, request, user_id, *args, **kwargs):
        if not self.has_change_permission(request):
            raise PermissionDenied

        user = self.get_object(request, unquote(user_id))
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(user_id),
            })

        if request.method != 'POST':
            form = UserStatusChangeForm()
            ## if the user is active, preselect deactivation and vice versa
            form.initial['status_action'] = (UserStatusChangeForm.STATUS_ITEMS[UserStatusChangeForm.DEACTIVATE]
                                             if user.is_active else
                                             UserStatusChangeForm.STATUS_ITEMS[UserStatusChangeForm.ACTIVATE])
        else:
            form = UserStatusChangeForm(request.POST)
            if form.is_valid():
                try:
                    form.save(user)
                except:
                    # If save() raises, the form will a have a non field error
                    # containing an informative message.
                    pass
                else:
                    self.message_user(request, 'User status changed successfully')
                    url = reverse(
                        '%s:%s_%s_changelist' % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),)
                    return HttpResponseRedirect(url)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['change_user'] = user
        context['title'] = 'Change User Status'

        return TemplateResponse(request, 'admin/user_change_status.html', context)
