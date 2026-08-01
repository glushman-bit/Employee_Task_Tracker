from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from config.settings import AUTH_USER_MODEL


class Employee(models.Model):
    """Модель сотрудника."""

    STATUS_AT_WORK = 'На работе'
    STATUS_VOCATION = 'Отпуск'
    STATUS_SICK_LEAVE = 'Больничный'
    STATUS_DAY_OFF = 'Выходной'

    CHOICES_STATUS = [
        (STATUS_AT_WORK, 'На работе'),
        (STATUS_VOCATION, 'Отпуск'),
        (STATUS_SICK_LEAVE, 'Больничный'),
        (STATUS_DAY_OFF, 'Выходной'),
    ]

    first_name = models.CharField(max_length=150, blank=True, verbose_name='Имя')
    middle_name = models.CharField(max_length=150, blank=True, default='', verbose_name='Отчество')
    second_name = models.CharField(max_length=150, blank=True, default='', verbose_name='Фамилия')
    position = models.CharField(max_length=150, blank=True, default='', verbose_name='Должность')
    phone_number = PhoneNumberField(blank=True, null=True, verbose_name='Телефон', help_text='Укажите номер телефона')
    email = models.EmailField(
        unique=True,
        verbose_name="Email сотрудника",
        help_text="Укажите Email",
    )
    status = models.CharField(max_length=15, choices=CHOICES_STATUS, default=STATUS_AT_WORK, verbose_name='статус')
    owner = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name="Руководитель",
        help_text="Укажите руководителя",
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    @property
    def full_name(self):
        """Собираем ФИО в одну строку."""

        name_list = [self.second_name, self.first_name, self.middle_name]
        result = " ".join(filter(None, name_list)).strip()

        return result if result else 'ФИО не указано'

    def __str__(self):
        return self.full_name


class Task(models.Model):
    """Модель задачи."""

    STATUS_CREATED = 'Создана'
    STATUS_RUNNING = 'Выполняется'
    STATUS_COMPLETED = 'Завершена'

    CHOICES_STATUS = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_RUNNING, 'Выполняется'),
        (STATUS_COMPLETED, 'Завершена'),
    ]

    PRIORITY_LOW = 'Низкий'
    PRIORITY_MEDIUM = 'Средний'
    PRIORITY_HIGH = 'Высокий'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Низкий'),
        (PRIORITY_MEDIUM, 'Средний'),
        (PRIORITY_HIGH, 'Высокий'),
    ]

    title = models.CharField(
        max_length=100,
        verbose_name='Название задачи',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание задачи',
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='subtasks',
        verbose_name='Связанная задача',
    )
    performer = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='tasks',
        verbose_name='Исполнитель задачи',
    )
    deadline = models.DateTimeField(verbose_name='Срок выполнения', help_text='Укажите дату и время завершения задачи')
    status = models.CharField(
        max_length=30, choices=CHOICES_STATUS, default=STATUS_CREATED, verbose_name='Статус задачи'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменена')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')
    owner = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Руководитель',
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM, verbose_name='Приоритет'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        if self.performer:
            return f"{self.title} ({self.performer})"
        return f"{self.title} (исполнитель не назначен)"

    @property
    def is_overdue(self):
        """Определение статуса просроченного задания."""

        return self.status != self.STATUS_COMPLETED and self.deadline < timezone.now()

    def save(self, *args, **kwargs):
        """Автоматическая установка времени завершения задачи при установке статуса STATUS_COMPLETED."""

        if self.status == self.STATUS_COMPLETED:
            if self.completed_at is None:
                self.completed_at = timezone.now()

        else:
            self.completed_at = None

        super().save(*args, **kwargs)
