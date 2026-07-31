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
        blank=True,
        null=True,
        verbose_name='Phone Number',
        help_text='Введите номер телефона',
    )
    email_verification_token = models.UUIDField(
        default=uuid.uuid4,
        blank=True,
        null=True,
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
