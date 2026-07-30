from django.contrib.auth.models import PermissionsMixin
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Проверка, что пользователь является владельцем."""

    message = "Вы не являетесь владельцем."

    def has_object_permission(self, request, view, obj):
        """Метод проверки владельца."""

        if obj.owner == request.user:
            return True

        return False
