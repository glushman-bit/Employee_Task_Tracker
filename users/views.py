from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ModelViewSet
from .serializer import UserSerializer, UserCreateSerializer
from .permissions import IsProfile

from users.models import User


class UserViewSet(ModelViewSet):
    """Класс работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Получение прав доступа для изменения профиля пользователя."""

        if self.action in ['update', 'partial_update']:
            self.permission_classes = (IsProfile,)

        return super().get_permissions()


class UserCreateAPIView(CreateAPIView):
    """Класс создания пользователя."""

    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]



