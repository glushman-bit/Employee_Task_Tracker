from django.contrib import admin

from employees.models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Административная панель для сотрудников."""

    list_display = ('full_name', 'position', 'owner',)
    search_fields = ('owner',)
    list_filter = ('owner', 'position',)
    ordering = ('position',)
