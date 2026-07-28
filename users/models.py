import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    """Класс пользователей."""

    username = None
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Введите Email',
    )
    phone_number = PhoneNumberField(
        unique=True,
        blank=True,
        null=True,
        verbose_name='Phone Number',
        help_text='Введите номер телефона',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
        help_text='Дата создания',
    )
    email_verification_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='Токен подтверждения email',
    )


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
