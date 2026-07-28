import os

from django.core.mail import send_mail

from config.settings import DEFAULT_FROM_EMAIL


def send_verification_email(user):
    """Функция отправки письма для верификации."""

    link = f'{os.getenv('HOST')}/users/verify/{user.email_verification_token}/'

    send_mail(
        subject='Подтверждение email',
        message=f'Подтверждение email: {link}',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
