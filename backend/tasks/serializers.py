from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "owner",
            "status",
            "due_date",
            "notes",
            "created_at",
            "updated_at"
        ]
