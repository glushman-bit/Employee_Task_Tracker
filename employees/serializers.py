from rest_framework.serializers import ModelSerializer
from employees.models import Employee


class EmployeeSerializer(ModelSerializer):
    """Сериалайзер вывода сотрудников."""

    class Meta:
        model = Employee
        fields = ('full_name', 'position', 'status', 'phone_number', 'email',)


class EmployeeCreateSerializer(ModelSerializer):
    """Сериализатор создания сотрудника."""

    class Meta:
        model = Employee
        fields = ('first_name', 'second_name', 'middle_name', 'position', 'status', 'phone_number', 'email',)