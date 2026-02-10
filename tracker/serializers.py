from rest_framework import serializers

from .models import Employee, Task


class EmployeeSerializer(serializers.ModelSerializer):
    load = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    assignee_detail = EmployeeSerializer(source="assignee", read_only=True)
    subtasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = "__all__"

    def get_subtasks_count(self, obj):
        return obj.subtasks.count()

    def validate_depends_on(self, value):
        task_id = self.instance.id if self.instance else None

        if task_id and any(dep.id == task_id for dep in value):
            raise serializers.ValidationError("Задача не может зависеть от самой себя.")
        return value

    def validate_parent(self, value):
        if self.instance and value and value.id == self.instance.id:
            raise serializers.ValidationError(
                "Задача не может быть родителем самой себе."
            )
        return value


class EmployeeTaskSerializer(serializers.ModelSerializer):
    tasks = serializers.StringRelatedField(many=True, read_only=True)
    active_tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ["id", "full_name", "position", "active_tasks_count", "tasks"]
