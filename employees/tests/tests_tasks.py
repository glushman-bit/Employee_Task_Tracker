from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from employees.models import Task
from users.models import User

from .base_setup import EmployeesTasksSetUp


class TasksTest(EmployeesTasksSetUp):
    """TestsCase для задач."""

    def test_create_task_without_performer(self):
        """Тест создания задачи без исполнителя."""

        url = reverse('employees:task-list')
        data = {
            'title': 'test',
            'status': Task.STATUS_CREATED,
            'deadline': timezone.now() + timedelta(days=2),
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)
        self.assertEqual(Task.objects.filter(status=Task.STATUS_CREATED).count(), 2)
        self.assertEqual(Task.objects.filter(status=Task.STATUS_RUNNING).count(), 1)

    def test_update_task(self):
        """Тест изменения задачи."""

        url = reverse('employees:task-detail', args=[self.task1.id])
        data = {
            'performer': self.employee1.id,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.performer, self.employee1)

    def test_retrieve_task(self):
        """Тест просмотра задачи."""

        url = reverse('employees:task-detail', args=[self.task1.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], self.task1.status)

    def test_list_tasks(self):
        """Тест просмотра списка задач."""

        url = reverse('employees:task-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        # Проверка пагинации
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

    def test_delete_task(self):
        """Тест удаления задачи."""

        url = reverse('employees:task-detail', args=[self.task1.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_not_add_employee_not_at_work(self):
        """Тест невозможности назначить сотрудника не на работе."""

        url = reverse('employees:task-detail', args=[self.task1.pk])
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, {'performer': self.employee2.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['performer'][0], 'Нельзя назначить задачу сотруднику, который сейчас не находится на работе.'
        )

    def test_not_view_list_tasks_without_authenticate(self):
        """Тест невозможности просмотра списка сотрудников неавторизованному пользователю."""

        url = reverse('employees:task-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get('detail'), 'Учетные данные не были предоставлены.')

    def test_user_cannot_see_other_user_tasks(self):
        """Проверка изоляции задач между пользователями."""

        other_user = User.objects.create(email='user2@test.pro')

        other_task = Task.objects.create(
            title='Чужая задача',
            description='',
            status=Task.STATUS_CREATED,
            deadline=timezone.now() + timedelta(days=1),
            owner=other_user,
        )

        url = reverse('employees:task-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        task_ids = [task['id'] for task in response.data['results']]

        self.assertNotIn(other_task.id, task_ids)

    def test_user_cannot_retrieve_other_user_task(self):
        """Проверка невозможности просмотра чужой задачи."""

        other_user = User.objects.create(email='user2@test.pro')

        other_task = Task.objects.create(
            title='Чужая задача',
            status=Task.STATUS_CREATED,
            deadline=timezone.now() + timedelta(days=1),
            owner=other_user,
        )

        url = reverse('employees:task-detail', args=[other_task.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_views_task_with_subtask(self):
        """Тест вывода данных о задачах и их подзадачах."""

        url = reverse('employees:statistics-tasks')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
