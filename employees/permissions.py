from typing import Any
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOwner(BasePermission):
    """Проверка, что пользователь является владельцем."""

    message = "Вы не являетесь владельцем."

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Метод проверки владельца."""

        if obj.owner == request.user:
            return True

        return False
