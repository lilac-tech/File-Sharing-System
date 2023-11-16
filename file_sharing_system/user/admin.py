from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm

# Register your models here.

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ['id', 'name', 'last_login']
    list_filter = ['admin']
    readonly_fields = ['last_login', 'date_joined']
    fieldsets = (
        (None, {'fields': ('id', 'name', 'password', 'division', 'last_login', 'date_joined')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('admin','staff')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id', 'name', 'password')}
        ),
    )
    search_fields = ['id', 'name']
    ordering = ['id']
    filter_horizontal = ()


admin.site.register(User, UserAdmin)