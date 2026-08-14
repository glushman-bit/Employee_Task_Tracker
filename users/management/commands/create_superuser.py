import os
from typing import Any

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Команда для создания суперпользователя."""

    help = "Создание суперпользователя"

    def handle(self, *args: Any, **options: Any) -> None:

        user, created = User.objects.get_or_create(email=os.getenv('ADMIN_EMAIL'))
        if created:
            user.set_password(os.getenv('ADMIN_PASSWORD'))
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            self.stdout.write(self.style.SUCCESS(f'Суперпользователь <{user.email}> успешно создан.'))
            user.save()

        else:
            self.stdout.write(self.style.WARNING(f'Суперпользователь <{user.email}> уже существует.'))
