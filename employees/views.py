from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from employees.models import Employee, Task
from employees.serializers import EmployeeSerializer, EmployeeCreateSerializer, TaskSerializer, TaskCreateSerializer


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
    """Класс вывода статистики."""

    def get(self, request):
        """Вывод количества сотрудников по руководителю."""

        return Response({
            'employees_count': request.user.employees.count(),
        })
