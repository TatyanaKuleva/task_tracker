from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tracker.apps import TrackerConfig

from .views import EmployeeViewSet, TaskViewSet

app_name = TrackerConfig.name
router = DefaultRouter()
router.register(r"tasks", TaskViewSet)
router.register(r"employees", EmployeeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
