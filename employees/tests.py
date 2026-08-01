from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
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
            status='На работе',
            phone_number='',
            email='test_Pronin@sky.pro',
            owner=self.user,
        )
        self.employee2 = Employee.objects.create(
            first_name='Артем',
            second_name='Павлов',
            middle_name='',
            position='Тестировщик',
            status='На работе',
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


class EmployeesTest(EmployeesTasksSetUp):
    """TestsCase для сотрудников."""

    def test_create_employee(self):
        """Тест создания сотрудника."""

        url = reverse('employees:employee-list')
        data = {
            'first_name': 'Алексей',
            'second_name': 'Иванов',
            'middle_name': '',
            'position': 'Креативщик',
            'status': 'На работе',
            'phone_number': '',
            'email': 'test_Ivanov@sky.pro',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['first_name'], data['first_name'])
        self.assertEqual(response.json()['position'], data['position'])
        self.assertEqual(response.json()['email'], data['email'])
        self.assertEqual(Employee.objects.count(), 3)

        employee = Employee.objects.latest('id')
        self.assertEqual(employee.second_name, 'Иванов')
        self.assertEqual(employee.owner, self.user)

    def test_update_employee(self):
        """Тест на редактирование сотрудника."""

        url = reverse('employees:employee-detail', args=[self.employee1.pk])
        data = {
            'first_name': 'Петр',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get('first_name'), 'Петр')

    def test_retrieve_employee(self):
        """Тест на просмотр сотрудника. Проверка поля full_name."""

        url = reverse('employees:employee-detail', args=[self.employee1.pk])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'],'Пронин Иван')

    def test_delete_employee(self):
        """Тест на удаление сотрудника."""

        url = reverse('employees:employee-detail', args=[self.employee1.pk])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_view_list_employees(self):
        """Тест просмотра списка сотрудников."""

        url = reverse('employees:employee-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('count'), Employee.objects.count())
        # Проверка пагинации
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

    def test_not_view_list_without_authenticate(self):
        """Тест невозможности просмотра списка сотрудников неавторизованному пользователю."""

        url = reverse('employees:employee-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get('detail'), 'Учетные данные не были предоставлены.')

