from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Класс вывода пользователей в админке."""

    model = User

    list_display = ('id', 'email', 'is_staff', 'is_active', 'date_joined',)
    search_fields = ('email',)
    list_filter = ('is_staff', 'is_active', 'is_superuser',)
    ordering = ('email',)
    readonly_fields = ('date_joined', 'email_verification_token',)
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2',),
            },
        ),
    )
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'password',
                )
            }
        ),
        (
            'Права доступа',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            }
        ),
        (
            'Дополнительно',
            {
                'fields': (
                    'phone_number',
                    'email_verification_token',
                    'date_joined',
                )
            }
        ),
    )