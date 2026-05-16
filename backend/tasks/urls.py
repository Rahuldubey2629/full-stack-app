from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, app_config, health_live, health_ready

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("health/live", health_live),
    path("health/ready", health_ready),
    path("config", app_config),
    path("", include(router.urls))
]
