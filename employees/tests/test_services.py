from django.utils import timezone
from datetime import timedelta
from employees.models import Employee, Task
from users.models import User
from .base_setup import EmployeesTasksSetUp
from employees.services import (
    StatisticsService,
    EmployeesSearchService,
    ImportantTaskService,
)


class StatisticsServiceTest(EmployeesTasksSetUp):
    """Тесты статистики."""

    def test_get_employees_at_work(self):
        """Проверка количества сотрудников на работе."""

        service = StatisticsService(self.user)
        result = service.get_employees_at_work()

        self.assertEqual(result['Количество сотрудников на работе'], 1)
        self.assertEqual(result['Данные о сотрудниках'][0]['id'], self.employee1.id)

    def test_employee_off(self):
        """Проверка количества отсутствующих сотрудников."""

        service = StatisticsService(self.user)
        result = service.get_employee_off()

        self.assertEqual(result['Количество отсутствующих сотрудников'], 1)
        self.assertEqual(result['Данные о сотрудниках'][0]['id'], self.employee2.id)


    def test_employee_workload(self):
        """Проверка загрузки сотрудников.
            Завершенные задачи не учитываются."""

        Task.objects.create(
            title='Завершенная',
            performer=self.employee1,
            status=Task.STATUS_COMPLETED,
            deadline=timezone.now() + timedelta(days=2),
            owner=self.user,
        )

        service = StatisticsService(self.user)
        result = service.get_employee_workload()

        employee = next(
            item for item in result
            if item['id'] == self.employee1.id
        )

        self.assertEqual(employee['active_tasks'], 1)
        self.assertEqual(len(employee['tasks']), 1)


class EmployeesSearchServiceTest(EmployeesTasksSetUp):
    """Тесты поиска сотрудников для выполнения задач."""

    def test_find_employee_with_min_tasks(self):
        """Тест, что сотрудник с минимальной загрузкой попадает в результат."""

        employee3 = Employee.objects.create(
            first_name='Сергей',
            second_name='Иванов',
            middle_name='',
            position='Программист',
            status=Employee.STATUS_AT_WORK,
            email='test@test.pro',
            owner=self.user,
        )

        service = EmployeesSearchService(self.user)
        result = service.get_available_employees_at_work(self.task1.id)

        employee_id = [
            employee.id
            for employee in result
        ]

        self.assertIn(employee3.id, employee_id)

    def test_get_performer_parent_task(self):
        """Тест возможности выбора исполнителя родительской задачи,
        если у него на 2 активные задачи больше, чем у наименее загруженного сотрудника."""

        self.task1.performer = self.employee1
        self.task1.save()

        Task.objects.create(
            title='Дополнительная задача 1',
            performer=self.employee1,
            status=Task.STATUS_RUNNING,
            deadline=timezone.now() + timedelta(days=2),
            owner=self.user,
        )
        employee3 = Employee.objects.create(
            first_name='Сергей',
            second_name='Иванов',
            middle_name='',
            position='Программист',
            status=Employee.STATUS_AT_WORK,
            email='test@test.pro',
            owner=self.user,
        )
        Task.objects.create(
            title='Дополнительная задача 2',
            performer=employee3,
            status=Task.STATUS_RUNNING,
            deadline=timezone.now() + timedelta(days=2),
            owner=self.user,
        )

        service = EmployeesSearchService(self.user)
        result = service.get_available_employees_at_work(self.task2.id)

        employee_id = [
            employee.id
            for employee in result
        ]

        self.assertIn(self.employee1.id, employee_id)

        employee = next(
            employee
            for employee in result
            if employee.id == self.employee1.id
        )

        self.assertEqual(employee.reason, 'Исполнитель родительской задачи')

    def test_parent_task_performer_not_selected_if_more_than_two_tasks(self):
        """Тест не возможности выбора исполнителя родительской задачи,
        если у него более 3 активных задач."""

        self.task1.performer = self.employee1
        self.task1.save()

        Task.objects.create(
            title='Дополнительная задача 1',
            performer=self.employee1,
            status=Task.STATUS_RUNNING,
            deadline=timezone.now() + timedelta(days=2),
            owner=self.user,
        )
        Task.objects.create(
            title='Дополнительная задача 2',
            performer=self.employee1,
            status=Task.STATUS_RUNNING,
            deadline=timezone.now() + timedelta(days=2),
            owner=self.user,
        )
        self.employee3 = Employee.objects.create(
            first_name='Сергей',
            second_name='Иванов',
            middle_name='',
            position='Программист',
            status=Employee.STATUS_AT_WORK,
            email='test@test.pro',
            owner=self.user,
        )
        Task.objects.create(
            title='Дополнительная задача 3',
            performer=self.employee3,
            status=Task.STATUS_RUNNING,
            deadline=timezone.now() + timedelta(days=2),
            owner=self.user,
        )

        service = EmployeesSearchService(self.user)
        result = service.get_available_employees_at_work(self.task2.id)

        employee_id = [
            employee.id
            for employee in result
        ]

        self.assertNotIn(self.employee1.id, employee_id)
        self.assertIn(self.employee3.id, employee_id)

        employee = next(
            employee
            for employee in result
            if employee.id == self.employee3.id
        )

        self.assertEqual(employee.reason, 'Минимальная загрузка')


class ImportantTaskServiceTest(EmployeesTasksSetUp):
    """Тесты вывода задач"""

    def test_get_important_tasks_queryset_returns_parent_task(self):
        """Тест, что родительская задача с выполняемой подзадачей определяется как важная."""

        service = ImportantTaskService(self.user)
        tasks = service.get_important_tasks_queryset()

        self.assertEqual(tasks.count(), 1)
        self.assertEqual(tasks.first(), self.task1)


    def test_created_task_with_running_subtask(self):
        """Проверка поиска задач с выполняемыми подзадачами."""

        service = ImportantTaskService(self.user)
        result = service.get_task_in_created_with_subtasks_in_running()

        self.assertEqual(result['Количество задач'], 1)
        self.assertEqual(result['Задачи'][0]['id'], self.task1.id)

    def test_get_important_tasks_returns_task_with_available_employees(self):
        """Важная задача возвращается с доступными сотрудниками."""

        service = ImportantTaskService(self.user)
        result = service.get_important_tasks()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Важная задача"], self.task1.title)
        self.assertEqual(result[0]["ФИО сотрудника"], [self.employee1.full_name])
