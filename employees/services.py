from .serializers import StatisticEmployeesSerializer, StatisticSerializer, SubtasksRunningSerializer
from .models import Employee, Task
from django.db.models import Count, Q, Prefetch


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
                # parent_task__status=Task.STATUS_RUNNING,
                subtasks__status=Task.STATUS_RUNNING,
            ).distinct()
        )

        serializer = SubtasksRunningSerializer(tasks, many=True)

        return {
            "Количество задач": tasks.count(),
            "Задачи": serializer.data,
        }
