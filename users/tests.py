import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserTestCase(APITestCase):
    """TestCase для пользователей."""

    def setUp(self):

        self.user1 = User.objects.create(email='user1@test.pro')
        self.user1.set_password('12345')
        self.user1.save()
        self.user2 = User.objects.create(email='user2@test.pro')
        self.user2.set_password('12345')
        self.user2.save()

    def test_create_user(self):
        """Тест создания пользователя."""

        url = reverse('users:register')
        data = {
            'email': 'user3@test.pro',
            'password': '12345',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.first()
        self.assertEqual(user.email, 'user1@test.pro')
        self.assertEqual(user.check_password('12345'), True)
        self.assertEqual(User.objects.all().count(), 3)

    def test_view_profile(self):
        """Тест на просмотр своего профиля."""

        url = reverse('users:users-detail', args=[self.user1.pk])
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user1.email)

    def test_update_own_profile(self):
        """Тест редактирования своего профиля."""

        url = reverse('users:users-detail', args=[self.user1.pk])
        self.client.force_authenticate(user=self.user1)
        data = {'email': 'test_2@test.pro'}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, 'test_2@test.pro')

    def test_view_other_profile(self):
        """Тест просмотр чужого профиля."""

        url = reverse('users:users-detail', args=[self.user2.pk])
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_views_list_users(self):
        """Просмотр списка пользователей."""

        url = reverse('users:users-list')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', response.data['results'][0])

        # Проверка пагинации списка
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

    def test_views_list_users_is_staff(self):
        """Просмотр списка пользователей суперпользователем."""

        url = reverse('users:users-list')
        user = User.objects.create(email='super@test.py', is_staff=True)
        user.set_password('12345')
        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_send_email_verify(self):
        """Тест отправки письма верификации."""

        user = User.objects.create(
            email='super@test.py',
            password='12345',
            is_active=True,
        )

        url = reverse(
            'users:verify',
            args=[user.email_verification_token]
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertIsNone(user.email_verification_token)
        self.assertEqual(response.data['message'], 'Email успешно подтвержден')

    def test_verify_invalid_token(self):
        """Тест на недействительный токен после верификации."""

        response = self.client.get(reverse('users:verify', args=[uuid.uuid4()]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
