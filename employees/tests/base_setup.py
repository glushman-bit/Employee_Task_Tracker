from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Employee, Task
from users.models import User


class EmployeesTasksSetUp(APITestCase):
    """Базовый класс подготовки тестов."""

    def setUp(self):

        self.user = User.objects.create(email='user1@test.pro')
        self.employee1 = Employee.objects.create(
            first_name='Иван',
            second_name='Пронин',
            middle_name='',
            position='IТ Прогер',
            status=Employee.STATUS_AT_WORK,
            phone_number='',
            email='test_Pronin@sky.pro',
            owner=self.user,
        )
        self.employee2 = Employee.objects.create(
            first_name='Артем',
            second_name='Павлов',
            middle_name='',
            position='Тестировщик',
            status=Employee.STATUS_DAY_OFF,
            phone_number='+79001234567',
            email='test_Pavlov@sky.pro',
            owner=self.user,
        )
        self.task1 = Task.objects.create(
            title='Тест_1',
            description='Тестирование',
            parent_task=None,
            performer=None,
            status=Task.STATUS_CREATED,
            deadline=timezone.now() + timedelta(days=2),
            owner=self.user,
        )
        self.task2 = Task.objects.create(
            title='Тест_2',
            description='',
            parent_task=self.task1,
            performer=self.employee1,
            status=Task.STATUS_RUNNING,
            deadline=timezone.now() + timedelta(days=2),
            owner=self.user,
        )
