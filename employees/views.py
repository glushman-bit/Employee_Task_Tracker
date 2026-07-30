from django.db.models import Count, Q, Prefetch
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from employees.models import Employee, Task
from employees.serializers import (EmployeeSerializer,
                                   EmployeeCreateSerializer,
                                   TaskSerializer,
                                   TaskCreateSerializer,
                                   StatisticSerializer,
                                   StatisticEmployeesSerializer,)


class EmployeeViewSet(ModelViewSet):
    """Класс работы с сотрудниками."""

    def get_serializer_class(self):
        """Переопределение сериалайзера в зависимости от действия."""

        if self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateSerializer

        return EmployeeSerializer

    def get_queryset(self):
        """Фильтруем вывод списка сотрудников по руководителю."""

        if not self.request.user.is_authenticated:
            return Employee.objects.none()

        return Employee.objects.filter(owner=self.request.user)


    def perform_create(self, serializer):
        """Автоматическая установка руководителя при создании."""

        serializer.save(owner=self.request.user)


class TaskViewSet(ModelViewSet):
    """Класс для работы с задачами."""

    def get_serializer_class(self):
        """Переопределение сериалайзера в зависимости от действия."""

        if self.action in ['create', 'update', 'partial_update']:
            return TaskCreateSerializer

        return TaskSerializer

    def get_queryset(self):
        """Фильтруем вывод списка задач по руководителю."""

        if not self.request.user.is_authenticated:
            return Task.objects.none()

        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Автоматическая установка руководителя/владельца при создании."""

        serializer.save(owner=self.request.user)


class StatisticsAPIView(APIView):
    """Класс вывода статистики по количеству сотрудников."""

    def get_employees_at_work(self, request):
        """Количество сотрудников."""

        employees = request.user.employees.filter(
            status=Employee.STATUS_AT_WORK
        )

        serializer = StatisticEmployeesSerializer(employees, many=True)

        return {
        "Количество сотрудников на работе": employees.count(),
        "Данные о сотрудниках": serializer.data,
        }


    def get_employee_off(self, request):
        """Количество сотрудников не на работе."""

        employees = request.user.employees.filter(
            status__in=[Employee.STATUS_VOCATION, Employee.STATUS_SICK_LEAVE, Employee.STATUS_DAY_OFF]
        )

        serializer = StatisticEmployeesSerializer(employees, many=True)

        return {
        "Количество сотрудников не на работе": employees.count(),
        "Данные о сотрудниках": serializer.data,
        }

    def get(self, request):
        """Вывод количества сотрудников по руководителю."""

        return Response({
            'Общее количество сотрудников': request.user.employees.count(),
            'Сотрудники на работе': self.get_employees_at_work(request),
            'Отсутствуют': self.get_employee_off(request),

        })


class EmployeeWorkloadAPIView(APIView):
    """Запрашивает из БД список сотрудников и их задачи, отсортированный по количеству активных задач."""

    def get_employee_workload(self, request):

        employees = Employee.objects.filter(
            owner=request.user,
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

    def get(self, request):
        """Вывод статистики."""

        return Response({
            'employee_workload': self.get_employee_workload(request),
        })
