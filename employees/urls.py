from django.urls import path
from rest_framework.routers import SimpleRouter

from employees.apps import EmployeesConfig
from employees.views import EmployeeViewSet, StatisticsAPIView

app_name = EmployeesConfig.name

router = SimpleRouter()
router.register(r'', EmployeeViewSet, basename="employee")

urlpatterns = [
    path('statistics/', StatisticsAPIView.as_view(), name='statistics'),
]
urlpatterns += router.urls
