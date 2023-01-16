from django.contrib import admin

from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

from crm.models import hzUserInfo, hzUserEvents

from crm.forms import CustomUserCreationForm, CustomUserChangeForm


class InlinehzUserInfo(admin.StackedInline):
    model = hzUserInfo


class InlinehzUserEvents(admin.StackedInline):
    model = hzUserEvents


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    inlines = [InlinehzUserInfo, InlinehzUserEvents, ]



admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(hzUserInfo)
class hzUserInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(hzUserEvents)
class hzUserEventsAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'title', 'hz_user')
    # list_editable = ('external_id', 'state',)

