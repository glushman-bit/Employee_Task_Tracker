from django.urls import reverse
from rest_framework import status

from employees.models import Employee, Task
from users.models import User
from .base_setup import EmployeesTasksSetUp


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
        self.assertEqual(response.data['first_name'], 'Петр')

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

    def test_not_view_list_employees_without_authenticate(self):
        """Тест невозможности просмотра списка сотрудников неавторизованному пользователю."""

        url = reverse('employees:employee-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get('detail'), 'Учетные данные не были предоставлены.')

    def test_user_cannot_see_other_user_employees(self):
        """Проверка изоляции сотрудников между пользователями."""

        other_user = User.objects.create(email='user2@test.pro')

        other_employee = Employee.objects.create(
            first_name='Петр',
            second_name='Иванов',
            middle_name='',
            position='Разработчик',
            status=Employee.STATUS_AT_WORK,
            email='test@test.pro',
            owner=other_user,
        )

        url = reverse('employees:employee-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        employee_id = [
            employee['id']
            for employee in response.data['results']
        ]

        self.assertNotIn(other_employee.id, employee_id)

    def test_views_employees_at_work(self):
        """Тест вывода данных о сотрудниках на работе."""

        url = reverse('employees:statistics-employees')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['Общее количество сотрудников'], Employee.objects.count())

    def test_views_employees_workload(self):
        """Тест вывода данных о занятости сотрудников."""

        url = reverse('employees:statistics-workload')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
