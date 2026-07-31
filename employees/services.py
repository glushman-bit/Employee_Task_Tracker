from .serializers import StatisticEmployeesSerializer, StatisticSerializer, AvailableEmployeesAtWorkSerializer, SubtasksRunningSerializer
from .models import Employee, Task
from django.db.models import Count, Q, Prefetch, Min, Case, When, Value, CharField
from rest_framework.generics import get_object_or_404


class StatisticsService:
    """Класс вывода статистики."""

    def __init__(self, user):
        """Передача пользователя в конструктор."""

        self.user = user

    def get_employees_at_work(self):
        """Получение количества сотрудников."""

        employees = self.user.employees.filter(
            status=Employee.STATUS_AT_WORK
        )

        serializer = StatisticEmployeesSerializer(employees, many=True)

        return {
            "Количество сотрудников на работе": employees.count(),
            "Данные о сотрудниках": serializer.data,
        }

    def get_employee_off(self):
        """Получение количества отсутствующих сотрудников."""

        employees = self.user.employees.filter(
            status__in=[Employee.STATUS_VOCATION, Employee.STATUS_SICK_LEAVE, Employee.STATUS_DAY_OFF]
        )

        serializer = StatisticEmployeesSerializer(employees, many=True)

        return {
            "Количество отсутствующих сотрудников": employees.count(),
            "Данные о сотрудниках": serializer.data,
        }

    def get_employee_workload(self):
        """Получение списка сотрудников и их задач, отсортированных по количеству активных задач."""

        employees = Employee.objects.filter(
            owner=self.user,
        ).annotate(
            active_tasks=Count(
                'tasks', filter=Q(
                    tasks__status__in=[
                        Task.STATUS_CREATED,
                        Task.STATUS_RUNNING
                    ]
                )
            )
        ).prefetch_related(
            Prefetch(
                'tasks',
                queryset=Task.objects.filter(
                    status__in=[
                        Task.STATUS_CREATED,
                        Task.STATUS_RUNNING
                    ]
                )
            )
        )

        serializer = StatisticSerializer(employees, many=True)

        return serializer.data

    def get_task_in_created_with_subtasks_in_running(self):
        """Получение задач не взятых в работу, но имеющих подзадачи взятые в работу."""

        tasks = (
            Task.objects.filter(
                owner=self.user,
                status=Task.STATUS_CREATED,
                subtasks__status=Task.STATUS_RUNNING,
            ).distinct()
        )

        serializer = SubtasksRunningSerializer(tasks, many=True)

        return {
            "Количество задач": tasks.count(),
            "Задачи": serializer.data,
        }


class EmployeesSearchService:
    """Класс подбора сотрудников для выполнения задач."""

    def __init__(self, user):
        """Передача пользователя в конструктор."""

        self.user = user

    def get_available_employees_at_work(self, task_id):
        """Получение списка сотрудников, которые могут взять работы на исполнение.
           Выполняет поиск по наименее загруженным сотрудникам или сотруднику, выполняющему родительскую задачу,
           если ему назначено максимум на 2 задачи больше, чем у наименее загруженного сотрудника."""

        queryset = Employee.objects.filter(
            owner=self.user,
            status=Employee.STATUS_AT_WORK,
        ).annotate(
            tasks_count=Count(
                'tasks',
                filter=Q(tasks__status=Task.STATUS_RUNNING)
            )
        )

        task = get_object_or_404(Task, pk=task_id, owner=self.user)

        min_count = queryset.aggregate(min_count=Min('tasks_count'))['min_count']

        parent_employee_id = None

        if task.parent_task:
            parent_employee_id = task.parent_task.performer_id

        queryset = queryset.annotate(
            reason=Case(
                When(
                    id=parent_employee_id,
                    tasks_count__lte=min_count + 2,
                    then=Value("Исполнитель родительской задачи")
                ),
                When(
                    tasks_count=min_count,
                    then=Value("Минимальная загрузка")
                ),
                output_field=CharField(),
            )
        )

        available_employees  = queryset.filter(
            Q(tasks_count=min_count)
            |
            Q(
                id=parent_employee_id,
                tasks_count__lte=min_count + 2,
            )
        ).order_by('tasks_count')


        return available_employees
