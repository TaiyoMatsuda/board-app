from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class MyUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'family_name',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_guide', 'is_staff',
                                       'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'family_name', 'is_staff')
    list_filter = ( 'is_staff', 'is_superuser', 'is_guide', 'is_active', 'groups')
    search_fields = ('email', 'first_name', 'family_name')
    ordering = ('id',)


admin.site.register(models.User, MyUserAdmin)
admin.site.register(models.EventComment)
admin.site.register(models.Participant)
admin.site.register(models.Event)
