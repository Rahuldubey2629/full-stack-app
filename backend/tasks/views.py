import os

from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Task
from .serializers import TaskSerializer


@api_view(["GET"])
def health_live(_request):
    return Response({"status": "alive"})


@api_view(["GET"])
def health_ready(_request):
    return Response({"status": "ready", "environment": "production" if not settings.DEBUG else "development"})


@api_view(["GET"])
def app_config(_request):
    return Response(
        {
            "appName": settings.APP_NAME,
            "message": settings.APP_MESSAGE,
            "environment": "production" if not settings.DEBUG else "development",
            "hasSecretConfigured": bool(settings.APP_SECRET or os.getenv("APP_SECRET", "")),
            "apiVersion": "v1"
        }
    )


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.order_by("-updated_at")
    serializer_class = TaskSerializer
