from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import UserCreateAPIView, UserViewSet, VerificationEmailView

app_name = UsersConfig.name

router = SimpleRouter()
router.register(r'', UserViewSet, basename='users')

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('verify/<uuid:token>/', VerificationEmailView.as_view(), name='verify'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls
