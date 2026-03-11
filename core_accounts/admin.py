from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CoreUser


@admin.register(CoreUser)
class CoreUserAdmin(UserAdmin):
    """
    Full admin for the custom CoreUser (AbstractBaseUser).
    Exposes is_staff and role so superusers can grant admin access to others.
    """
    model = CoreUser

    list_display  = ('email', 'full_name', 'role', 'is_staff', 'is_superuser', 'is_active')
    list_filter   = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'full_name')
    ordering      = ('email',)

    # Fields shown when EDITING an existing user
    fieldsets = (
        (None,           {'fields': ('email', 'password')}),
        ('Personal',     {'fields': ('full_name',)}),
        ('Role',         {'fields': ('role',)}),
        ('Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    # Fields shown when CREATING a new user via the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2',
                       'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # CoreUser uses email, not username
    filter_horizontal = ('groups', 'user_permissions')
