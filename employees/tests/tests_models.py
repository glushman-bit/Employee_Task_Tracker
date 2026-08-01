from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Employee, Task
from users.models import User
from .base_setup import EmployeesTasksSetUp


class TaskModelTest(EmployeesTasksSetUp):
    """TestsCase для полей модели."""

    def test_completed_at_set_when_completed(self):
        """Проверка автоматической установки completed_at."""

        self.assertIsNone(self.task1.completed_at)

        self.task1.status = Task.STATUS_COMPLETED
        self.task1.save()

        self.task1.refresh_from_db()
        self.assertIsNotNone(self.task1.completed_at)

    def test_completed_at_clear_when_status_changed(self):
        """Проверка очистки completed_at при изменении статуса."""

        self.task1.status = Task.STATUS_COMPLETED
        self.task1.save()

        self.assertIsNotNone(self.task1.completed_at)

        self.task1.status = Task.STATUS_RUNNING
        self.task1.save()

        self.task1.refresh_from_db()

        self.assertIsNone(self.task1.completed_at)

    def test_is_overdue_true(self):
        """Проверка, что просроченная задача определяется корректно."""

        self.task1.deadline = timezone.now() - timedelta(days=1)
        self.task1.status = Task.STATUS_RUNNING
        self.task1.save()

        self.assertTrue(self.task1.is_overdue)

    def test_is_overdue_false_for_completed_task(self):
        """Завершенная задача не считается просроченной."""

        self.task1.deadline = timezone.now() - timedelta(days=1)
        self.task1.status = Task.STATUS_COMPLETED
        self.task1.save()

        self.assertFalse(self.task1.is_overdue)

    def test_create_task_with_past_deadline(self):
        """Тест невозможности создать задачу с прошедшим сроком."""

        url = reverse('employees:task-list')
        data ={
            'title': 'Просроченная задача',
            'status': Task.STATUS_CREATED,
            'deadline': timezone.now() - timedelta(days=1),
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Срок выполнения не может быть раньше текущего времени.',
            str(response.data)
        )
