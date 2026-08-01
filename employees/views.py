from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.serializers import IntegerField, Serializer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from employees.models import Employee, Task
from employees.serializers import (
    AvailableEmployeesAtWorkSerializer,
    EmployeeCreateSerializer,
    EmployeeSerializer,
    TaskCreateSerializer,
    TaskSerializer,
)
from employees.services import EmployeesSearchService, ImportantTaskService, StatisticsService


class EmployeeViewSet(ModelViewSet):
    """Класс работы с сотрудниками."""

    filter_backends = [DjangoFilterBackend, OrderingFilter,]
    ordering_fields = ['id', 'position',]
    filterset_fields = ['second_name', 'status', 'position',]
    ordering = ['id',]

    def get_serializer_class(self):
        """Переопределение сериалайзера в зависимости от действия."""

        if self.request.query_params.get('task_id') is not None:
            return AvailableEmployeesAtWorkSerializer

        if self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateSerializer

        return EmployeeSerializer

    def get_queryset(self):
        """Фильтруем вывод списка сотрудников по руководителю."""

        if not self.request.user.is_authenticated:
            return Employee.objects.none()

        serializer = TaskQueryParamSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        task_id = validated_data.get('task_id', None)

        if task_id:
            service = EmployeesSearchService(self.request.user)

            return service.get_available_employees_at_work(task_id)

        return Employee.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Автоматическая установка руководителя при создании."""

        serializer.save(owner=self.request.user)


class TaskQueryParamSerializer(Serializer):
    """Сериализатор валидации поля task_id. Проверяем, что это число."""

    task_id = IntegerField(required=False)


class TaskViewSet(ModelViewSet):
    """Класс для работы с задачами."""

    filter_backends = [DjangoFilterBackend, OrderingFilter,]
    ordering_fields = ['id', 'deadline', 'priority']
    filterset_fields = ['status', 'performer', 'parent_task',]
    ordering = ['id', ]

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


class StatisticsEmployeesAPIView(APIView):
    """Класс вывода статистики по количеству сотрудников."""

    def get(self, request):
        """Вывод статистики."""

        service = StatisticsService(request.user)

        return Response({
            'Общее количество сотрудников': request.user.employees.count(),
            'Сотрудники на работе': service.get_employees_at_work(),
            'Отсутствуют': service.get_employee_off(),
        })


class StatisticsEmployeeWorkloadAPIView(APIView):
    """Вывод статистики по сотрудникам и их задачам."""

    def get(self, request):
        """Вывод статистики."""

        service = StatisticsService(request.user)

        return Response({
            'Занятые сотрудники': service.get_employee_workload(),
        })


class StatisticsTasksWithSubtasks(APIView):
    """Вывод статистики по задачам не взятым в работу, но имеющим подзадачи взятые в работу."""

    def get(self, request):
        """Вывод статистики."""

        service = ImportantTaskService(request.user)

        return Response({
            'Не взятые в работу задачи, от которых зависят выполняемые': service.get_task_in_created_with_subtasks_in_running(),
        })


class ImportantTasksAPIView(APIView):
    """Вывод важных задач и рекомендуемых исполнителей."""

    def get(self, request):
        """Получение данных."""

        service = ImportantTaskService(request.user)

        tasks = service.get_important_tasks()

        return Response(tasks)
