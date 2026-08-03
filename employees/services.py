from typing import Any

from django.db.models import Case, CharField, Count, Min, Prefetch, Q, Value, When
from rest_framework.generics import get_object_or_404
from rest_framework.utils.serializer_helpers import ReturnList
from django.db.models import QuerySet

from .models import Employee, Task
from .serializers import (
    StatisticEmployeesSerializer,
    StatisticSerializer,
    SubtasksRunningSerializer,
)
from users.models import User


class StatisticsService:
    """Класс вывода статистики."""

    def __init__(self, user: User) -> None:
        """Передача пользователя в конструктор."""

        self.user = user

    def get_employees_at_work(self) -> dict[str, Any]:
        """Получение количества сотрудников."""

        employees = self.user.employees.filter(status=Employee.STATUS_AT_WORK)

        serializer = StatisticEmployeesSerializer(employees, many=True)

        return {
            "Количество сотрудников на работе": employees.count(),
            "Данные о сотрудниках": serializer.data,
        }

    def get_employee_off(self) -> dict[str, Any]:
        """Получение количества отсутствующих сотрудников."""

        employees = self.user.employees.filter(
            status__in=[Employee.STATUS_VOCATION, Employee.STATUS_SICK_LEAVE, Employee.STATUS_DAY_OFF]
        )

        serializer = StatisticEmployeesSerializer(employees, many=True)

        return {
            "Количество отсутствующих сотрудников": employees.count(),
            "Данные о сотрудниках": serializer.data,
        }

    def get_employee_workload(self) -> ReturnList:
        """Получение списка сотрудников и их задач, отсортированных по количеству активных задач."""

        employees = (
            Employee.objects.filter(
                owner=self.user,
            )
            .annotate(
                active_tasks=Count('tasks', filter=Q(tasks__status__in=[Task.STATUS_CREATED, Task.STATUS_RUNNING]))
            )
            .prefetch_related(
                Prefetch('tasks', queryset=Task.objects.filter(status__in=[Task.STATUS_CREATED, Task.STATUS_RUNNING]))
            )
        )

        serializer = StatisticSerializer(employees, many=True)

        return serializer.data


class EmployeesSearchService:
    """Класс подбора сотрудников для выполнения задач."""

    def __init__(self, user: User) -> None:
        """Передача пользователя в конструктор."""

        self.user = user

    def get_available_employees_at_work(self, task_id: int) -> QuerySet[Employee]:
        """Получение списка сотрудников, которые могут взять работы на исполнение.
        Выполняет поиск по наименее загруженным сотрудникам или сотруднику (со статусом "на работе"),
        выполняющему родительскую задачу, если ему назначено максимум на 2 задачи больше,
        чем у наименее загруженного сотрудника."""

        queryset = Employee.objects.filter(
            owner=self.user,
            status=Employee.STATUS_AT_WORK,
        ).annotate(
            tasks_count=Count(
                'tasks',
                filter=Q(
                    tasks__status__in=[
                        Task.STATUS_CREATED,
                        Task.STATUS_RUNNING,
                    ]
                ),
            )
        )

        task = get_object_or_404(Task, pk=task_id, owner=self.user)

        min_count = queryset.aggregate(min_count=Min('tasks_count'))['min_count']

        if min_count is None:
            return queryset.none()

        parent_employee_id = None

        if task.parent_task:
            parent_employee_id = task.parent_task.performer_id

        queryset = queryset.annotate(
            reason=Case(
                When(
                    id=parent_employee_id,
                    tasks_count__lte=min_count + 2,
                    then=Value("Исполнитель родительской задачи"),
                ),
                When(tasks_count=min_count, then=Value("Минимальная загрузка")),
                output_field=CharField(),
            )
        )

        available_employees = queryset.filter(
            Q(tasks_count=min_count)
            | Q(
                id=parent_employee_id,
                tasks_count__lte=min_count + 2,
            )
        ).order_by('tasks_count')

        return available_employees


class ImportantTaskService:
    """Класс вывода результата по поиску задач и сотрудников для их выполнения."""

    def __init__(self, user: User) -> None:
        """Передача пользователя в конструктор."""

        self.user = user

    def get_important_tasks_queryset(self) -> QuerySet[Task]:
        """Получение задач не взятых в работу, но имеющих выполняемые подзадачи."""

        tasks = Task.objects.filter(
            owner=self.user,
            status=Task.STATUS_CREATED,
            subtasks__status=Task.STATUS_RUNNING,
        ).distinct()

        return tasks

    def get_task_in_created_with_subtasks_in_running(self) -> dict[str, Any]:
        """Получение задач не взятых в работу, но имеющих подзадачи взятые в работу."""

        tasks = self.get_important_tasks_queryset()

        serializer = SubtasksRunningSerializer(tasks, many=True)

        return {
            "Количество задач": tasks.count(),
            "Задачи": serializer.data,
        }

    def get_important_tasks(self) -> list[dict[str, Any]]:

        tasks = self.get_important_tasks_queryset()

        result = []

        employees_service = EmployeesSearchService(self.user)

        for task in tasks:
            employees = employees_service.get_available_employees_at_work(task.id)

            result.append(
                {
                    "Важная задача": task.title,
                    "Срок": task.deadline,
                    "ФИО сотрудника": [employee.full_name for employee in employees],
                }
            )

        return result
