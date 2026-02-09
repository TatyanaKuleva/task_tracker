from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, EmployeeViewSet
from tracker.apps import TrackerConfig

app_name = TrackerConfig.name
router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'employees', EmployeeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]