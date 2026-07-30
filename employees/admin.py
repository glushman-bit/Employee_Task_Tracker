from django.contrib import admin

from employees.models import Employee, Task


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Административная панель для сотрудников."""

    list_display = ('full_name', 'position', 'owner', 'status',)
    search_fields = ('owner',)
    list_filter = ('owner', 'position',)
    ordering = ('position',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Административная панель для задач."""

    list_display = ('title', 'description', 'performer', 'deadline', 'status', 'created_at', 'owner', 'updated_at',)
    search_fields = ('title', 'performer', 'owner',)
    list_filter = ('title', 'performer', 'owner',)
