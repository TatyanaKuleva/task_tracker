import random
from django.core.management.base import BaseCommand
from users.models import User
from django.utils import timezone
from tracker.models import Task, Employee


class Command(BaseCommand):
    help = 'Заполняет базу данных 10 тестовыми задачами'

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(email='admin@example.com')

        Task.objects.all().delete()
        Employee.objects.all().delete()
        self.stdout.write(self.style.WARNING('Старые задачи удалены.'))

        positions = ['Frontend Developer', 'Backend Developer', 'QA Engineer', 'Project Manager']
        names = ['Иванов Иван', 'Петров Петр', 'Сидоров Алексей', 'Анна Кузнецова']
        emails = ['ivanov@mail.ru', 'petrov@mail.ru', 'sidorov@mail.ru', 'kuznecova@mail.ru']

        employees = []
        for email in emails:
            # username = name.split()[1].lower() + str(random.randint(1, 99))
            user, _ = User.objects.get_or_create(email=email)

            emp = Employee.objects.create(
                user=user,
                # full_name=names,
                position=random.choice(positions),
                department="IT Департамент"
            )
            employees.append(emp)

        self.stdout.write(self.style.SUCCESS(f"Создано {len(employees)} сотрудников."))

        tasks_pool = []
        statuses = ['new', 'in_progress', 'done', 'blocked']

        for i in range(1, 6):
            task = Task.objects.create(
                title=f"Родительская задача №{i}",
                description=f"Описание крупной цели №{i}",
                status=random.choice(statuses),
                priority=random.randint(1, 3),
                assignee=random.choice(employees),
                due_date=timezone.now() + timezone.timedelta(days=i * 2)
            )
            tasks_pool.append(task)


        self.stdout.write(self.style.SUCCESS("Задачи созданы и распределены!"))

        for i in range(1, 6):
            parent = random.choice(tasks_pool[:5])
            subtask = Task.objects.create(
                title=f"Подзадача №{i} (для {parent.id})",
                description=f"Детализация работы для задачи {parent.title}",
                parent=parent,
                status=random.choice(statuses),
                priority=random.randint(1, 3),
                assignee=random.choice(employees)
            )
            tasks_pool.append(subtask)


        for i in range(5, 10):
            target_task = tasks_pool[i]
            dependency = tasks_pool[i - 5]
            target_task.depends_on.add(dependency)

        self.stdout.write(self.style.SUCCESS(f'Успешно создано {Task.objects.count()} задач!'))
        self.stdout.write("---")
        self.stdout.write("Схема зависимостей:")
        for t in Task.objects.all():
            parent_info = f" -> Родитель: {t.parent.id}" if t.parent else ""
            deps_info = f" -> Зависит от: {[d.id for d in t.depends_on.all()]}" if t.depends_on.exists() else ""
            self.stdout.write(f"ID {t.id}: {t.title}{parent_info}{deps_info}")
