from rest_framework.permissions import BasePermission


class IsProfile(BasePermission):
    """Проверка, что пользователь является владельцем."""

    message = "Это не ваш профиль."

    def has_object_permission(self, request, view, obj):
        """Метод проверки владельца."""

        if obj == request.user:
            return True

        return False
