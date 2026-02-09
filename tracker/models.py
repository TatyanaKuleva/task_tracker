from django.db import models
from users.models import User


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    position = models.CharField(max_length=150, verbose_name="Должность")

    telegram_handle = models.CharField(max_length=100, blank=True, null=True, verbose_name="Телеграм")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отдел")
    hire_date = models.DateField(null=True, blank=True, verbose_name="Дата приема на работу")

    def __str__(self):
        return f"{self.full_name} ({self.position})"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"



class Task(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name="Родительская задача"
    )

    depends_on = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='blocked_tasks',
        verbose_name="Зависит от выполнения"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'Новая'),
            ('in_progress', 'В работе'),
            ('done', 'Завершена'),
            ('blocked', 'Заблокирована'),
        ],
        default='new', verbose_name="Статус"
    )

    priority = models.IntegerField(default=1, verbose_name="Важность")

    assignee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name="Исполнитель"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата и время завершения")

    def __str__(self):
        return f"[{self.id}] {self.title}"

    class Meta:
        ordering = ['-priority', 'due_date']
