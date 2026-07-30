from django.urls import path
from rest_framework.routers import SimpleRouter

from employees.apps import EmployeesConfig
from employees.views import EmployeeViewSet, StatisticsAPIView, TaskViewSet, EmployeeWorkloadAPIView


app_name = EmployeesConfig.name

router = SimpleRouter()

router.register(r'employees', EmployeeViewSet, basename="employee")
router.register(r'tasks', TaskViewSet, basename="task")

urlpatterns = [
    path('statistics/', StatisticsAPIView.as_view(), name='statistics'),
    path('statistics/workload/', EmployeeWorkloadAPIView.as_view(), name='workload'),
]
urlpatterns += router.urls
