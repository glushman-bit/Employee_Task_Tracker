from rest_framework import status
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users.models import User

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
