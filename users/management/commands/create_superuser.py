import os

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Команда для создания суперпользователя."""

    help = "Создание суперпользователя"

    def handle(self, *args, **options):
        user = User.objects.create(email=os.getenv('ADMIN_EMAIL'))
        user.set_password(os.getenv('ADMIN_PASSWORD'))
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        self.stdout.write(self.style.SUCCESS(f'Пользователь <{user.email}> успешно создан.'))
        user.save()
