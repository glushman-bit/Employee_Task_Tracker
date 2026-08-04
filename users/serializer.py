from typing import Any

from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    """Сериалайзер вывода данных о пользователях."""

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'phone_number',
            'date_joined',
        )
        extra_kwargs = {'id': {'read_only': True}}

    def to_representation(self, instance: Any) -> dict[Any, Any]:
        """Метод подмены null на текст."""

        representation = super().to_representation(instance)

        if representation.get('phone_number') is None:
            representation['phone_number'] = "Номер телефона не предоставлен."

        return representation


class UserCreateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data: dict[str, Any]) -> User:
        """Метод создания пользователя."""

        user = User(email=validated_data['email'], is_active=False)
        user.set_password(validated_data['password'])
        user.save()

        return user
