
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from employees.models import Employee, Task
from employees.serializers import (EmployeeSerializer,
                                   EmployeeCreateSerializer,
                                   TaskSerializer,
                                   TaskCreateSerializer,)
from employees.services import StatisticsService


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

        service = StatisticsService(request.user)

        return Response({
            'Не взятые в работу задачи, от которых зависят выполняемые': service.get_task_in_created_with_subtasks_in_running(),
        })


