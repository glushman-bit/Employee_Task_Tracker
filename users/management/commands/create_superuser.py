import os

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Команда для создания суперпользователя."""

    help = "Создание суперпользователя"

    def handle(self, *args, **options):

        user, create = User.objects.get_or_create(email=os.getenv('ADMIN_EMAIL'))
        if create:
            user.set_password(os.getenv('ADMIN_PASSWORD'))
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            self.stdout.write(self.style.SUCCESS(f'Суперпользователь <{user.email}> успешно создан.'))
            user.save()

        else:
            self.stdout.write(self.style.SUCCESS(f'Суперпользователь <{user.email}> уже существует.'))
