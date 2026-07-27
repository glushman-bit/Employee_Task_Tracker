from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс вывода пользователей в админке."""

    list_display = ('id', 'email', 'is_staff', 'is_active', 'created_at',)
    search_fields = ('email', 'created_at',)
    exclude = ('password',)
