from typing import Any

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.services import send_verification_email

from .serializer import UserCreateSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    """Класс работы с пользователями."""

    serializer_class = UserSerializer

    def get_queryset(self) -> QuerySet:
        """Получение прав доступа для изменения профиля пользователя.
        Пользователь может видеть и редактировать только себя,
        Администратор может видеть и редактировать всех."""

        if self.request.user.is_staff:
            return User.objects.all()

        return User.objects.filter(id=self.request.user.id)


class UserCreateAPIView(CreateAPIView):
    """Класс создания пользователя."""

    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Создание пользователя и отправка письма для подтверждения Email."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        print(user.email)
        print(user.email_verification_token)

        send_verification_email(user)

        return Response(
            {
                "email": user.email,
                "message": (
                    "Пользователь успешно зарегистрирован. "
                    "Проверьте электронную почту для подтверждения регистрации."
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class VerificationEmailView(APIView):
    """Подтверждение электронной почты."""

    permission_classes = [AllowAny]

    def get(self, request: Request, token: str) -> Response:
        user = get_object_or_404(User, email_verification_token=token)
        user.is_active = True
        user.email_verification_token = None
        user.save()

        return Response(
            {'message': 'Email успешно подтвержден'},
            status=status.HTTP_200_OK,
        )
