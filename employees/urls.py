from django.urls import path
from rest_framework.routers import SimpleRouter

from employees.apps import EmployeesConfig
from employees.views import (
    EmployeeViewSet,
    ImportantTasksAPIView,
    StatisticsEmployeesAPIView,
    StatisticsEmployeeWorkloadAPIView,
    StatisticsTasksWithSubtasks,
    TaskViewSet,
)

app_name = EmployeesConfig.name

router = SimpleRouter()

router.register(r'employees', EmployeeViewSet, basename="employee")
router.register(r'tasks', TaskViewSet, basename="task")

urlpatterns = [
    path('statistics/employees/', StatisticsEmployeesAPIView.as_view(), name='statistics-employees'),
    path('statistics/workload/', StatisticsEmployeeWorkloadAPIView.as_view(), name='statistics-workload'),
    path('statistics/tasks/', StatisticsTasksWithSubtasks.as_view(), name='statistics-tasks'),
    path('important-tasks/', ImportantTasksAPIView.as_view(), name='important-tasks'),
]
urlpatterns += router.urls
