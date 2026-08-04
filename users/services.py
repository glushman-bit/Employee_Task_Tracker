import os

from django.core.mail import send_mail

from config.settings import DEFAULT_FROM_EMAIL

from .models import User


def send_verification_email(user: User) -> None:
    """Функция отправки письма для верификации."""

    link = f'{os.getenv('HOST')}/users/verify/{user.email_verification_token}/'

    send_mail(
        subject='Регистрация в сервисе Employee_tracker.',
        message=f'Для подтверждения email, перейдите по ссылке: {link}',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
