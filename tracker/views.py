from django.db.models import Count, Min, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Employee, Task
from .serializers import (EmployeeSerializer, EmployeeTaskSerializer,
                          TaskSerializer)


class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @action(detail=False, methods=["get"], url_path="workload")
    def get_workload(self, request):
        """
        Возвращает список сотрудников, отсортированный по количеству активных задач.
        Эндпоинт: /api/employees/workload/
        """
        employees = Employee.objects.annotate(
            active_tasks_count=Count("tasks", filter=~Q(tasks__status="in_progress"))
        ).order_by("-active_tasks_count")

        serializer = EmployeeTaskSerializer(employees, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "priority", "assignee", "parent"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority"]

    def get_queryset(self):
        queryset = Task.objects.all()
        root_only = self.request.query_params.get("root_only")
        if root_only == "true":
            queryset = queryset.filter(parent__isnull=True)
        return queryset

    def get_base_critical_queryset(self):
        """Общая логика фильтрации задач со статусом 'new', блокирующие 'in_progress'"""
        return Task.objects.filter(
            status="new",
            blocked_tasks__status="in_progress"
        ).select_related("parent", "parent__assignee").distinct()
    #
    # @action(detail=False, methods=["get"])
    # def get_critical_blockers(self):
    #     # Получаем базовый QuerySet и работаем с ним
    #     qs = self.get_base_critical_queryset()
    #     # Можно добавить еще фильтрации здесь
    #     return Response(self.get_serializer(qs, many=True).data)
    #
    # @action(detail=False, methods=["get"])
    # def export_critical_data(self, request):
    #     # Используем тот же самый QuerySet, но фильтруем по-другому
    #     qs = self.get_base_critical_queryset().filter(priority=1)
    #     # ... логика экспорта ...


    # @action(detail=False, methods=["get"], url_path="critical-blockers")
    # def get_critical_blockers(self, request):
    #     """
    #     Задачи 'new', блокирующие 'in_progress'
    #     """
    #     critical_tasks = (
    #         Task.objects.filter(status="new", blocked_tasks__status="in_progress")
    #         .select_related("parent", "parent__assignee")
    #         .distinct()
    #     )
    #
    #     serializer = TaskSerializer(critical_tasks, many=True)
    #     return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="critical-blockers")
    def get_critical_blockers(self, request):
        """
        Задачи 'new', блокирующие 'in_progress'
        """
        qs_critical_blockers = self.get_base_critical_queryset()

        serializer = TaskSerializer(qs_critical_blockers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="suggested_employees_for_critical_task")
    def suggested_employees_for_critical_task(self, request):
        """
        подбирает сотрудников для задач не взятых в работу, от которых зависят задачи в работе по критериям:
        - минимум нагрузки
        - либо исполнитель родительской задачи, если у него максимум на 2 задачи больше, чем у минимально загруженного
        """
        employees_qs = Employee.objects.annotate(
            load=Count("tasks", filter=Q(tasks__status="in_progress"))
        ).order_by("load")

        if not employees_qs.exists():
            return Response({"error": "Нет сотрудников в базе"}, status=404)

        min_load = employees_qs.aggregate(Min("load"))["load__min"] or 0
        least_loaded_employees = list(employees_qs.filter(load=min_load))

        qs_critical_blockers = self.get_base_critical_queryset()

        results = []
        for task in qs_critical_blockers:
            suggested = list(least_loaded_employees)

            if task.parent and task.parent.assignee:
                p_assignee = employees_qs.filter(id=task.parent.assignee.id).first()
                if p_assignee and p_assignee not in suggested:
                    if p_assignee.load <= (min_load + 2):
                        suggested.append(p_assignee)

            task_data = self.get_serializer(task).data
            task_data["suggested_assignees"] = EmployeeSerializer(
                suggested, many=True
            ).data

            results.append(task_data)

        return Response(results)

    @action(detail=False, methods=["get"], url_path="priority-report")
    def get_priority_report(self, request):
        """
        Возвращает задачи с приоритетом 1.
        Формат: { "Важная задача": "Название", "Срок": "Дата", "ФИО сотрудника": ["ФИО"] }
        """
        tasks = Task.objects.filter(priority=1).select_related("assignee")

        report = []
        for task in tasks:
            assignees_names = [task.assignee.full_name] if task.assignee else []

            report.append(
                {
                    "Важная задача": task.title,
                    "Срок": (
                        task.due_date.strftime("%d.%m.%Y %H:%M")
                        if task.due_date
                        else "Срок не задан"
                    ),
                    "ФИО сотрудника": assignees_names,
                }
            )

        return Response(report)
