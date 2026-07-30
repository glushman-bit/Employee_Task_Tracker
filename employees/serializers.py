from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.serializers import ModelSerializer
from employees.models import Employee, Task


class EmployeeSerializer(ModelSerializer):
    """Сериалайзер вывода сотрудников."""

    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'position', 'status', 'phone_number', 'email',)


class EmployeeCreateSerializer(ModelSerializer):
    """Сериализатор создания сотрудника."""

    class Meta:
        model = Employee
        fields = ('first_name', 'second_name', 'middle_name', 'position', 'status', 'phone_number', 'email',)


class ParentTaskSerializer(ModelSerializer):
    """Класс вывода родительской задачи."""

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'priority',)


class TaskSerializer(ModelSerializer):
    """Сериалайзер вывода задач."""

    performer = EmployeeSerializer(read_only=True)
    parent_task = ParentTaskSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'parent_task', 'status', 'performer', 'deadline', 'priority',)


class TaskCreateSerializer(ModelSerializer):
    """Сериализатор создания задач."""

    class Meta:
        model = Task
        fields = ('title', 'description', 'parent_task', 'performer', 'deadline', 'priority', 'status',)

    def __init__(self, *args, **kwargs):
        """Инициализирует сериализатор и ограничивает доступный список исполнителей и задач."""

        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if request:
            self.fields['performer'].queryset = Employee.objects.filter(
                owner=request.user,
            )

            self.fields['parent_task'].queryset = Task.objects.filter(
                owner=request.user,
            )

    def validate_performer(self, employee):
        """Проверка статуса сотрудника."""

        if employee.status != Employee.STATUS_AT_WORK:
            raise ValidationError(
                "Нельзя назначить задачу сотруднику, который сейчас не находится на работе."
            )

        return employee

    def validate_deadline(self, value):
        """Проверка, что срок выполнения не находится в прошлом."""

        if value < timezone.now():
            raise ValidationError(
                {'deadline': 'Срок выполнения не может быть раньше текущего времени.'}
            )


class StatisticTasksSerializer(ModelSerializer):
    """Сериализатор вывода статистики по задачам."""

    class Meta:
        model = Task
        fields = ('id', 'title', 'status', 'deadline', 'priority',)


class StatisticSerializer(ModelSerializer):
    """Сериалайзер вывода статистики."""

    tasks = StatisticTasksSerializer(many=True, read_only=True)
    active_tasks = IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'active_tasks', 'tasks',)


class StatisticEmployeesSerializer(ModelSerializer):
    """Сериалайзер вывода статистики по сотрудникам."""

    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'position', 'status',)


class TaskShortSerializer(ModelSerializer):
    """Сериалайзер вывода сокращенных данных о задачах."""

    class Meta:
        model = Task
        fields = ('id', 'title', 'status', 'priority',)


class SubtasksRunningSerializer(ModelSerializer):
    """Сериалайзер вывода статистики по подзадачам."""

    running_subtasks = SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'title', 'status', 'running_subtasks',)

    def get_running_subtasks(self, obj):
        """Реализация поля 'running_subtasks'."""

        tasks = obj.subtasks.filter(
            status=Task.STATUS_RUNNING
        )

        return TaskShortSerializer(tasks, many=True).data
