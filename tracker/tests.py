from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from .models import Employee, Task

User = get_user_model()


class TaskAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="12345")
        self.employee = Employee.objects.create(full_name="Иван Иванов", user=self.user)
        self.task = Task.objects.create(
            title="Тестовая задача",
            description="Описание",
            status="new",
            priority=1,
            assignee=self.employee,
        )
        self.client = APIClient()
        self.client.login(email="test@test.com", password="12345")

        self.task_url = reverse("tracker:task-detail", args=[self.task.id])
        self.list_url = reverse("tracker:task-list")

    def test_create_task(self):
        data = {
            "title": "Новая задача",
            "description": "Описание задачи",
            "status": "new",
            "priority": 2,
            "assignee": self.employee.id,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Task.objects.last().title, "Тестовая задача")

    def test_retrieve_task(self):
        response = self.client.get(self.task_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.task.id)
        self.assertEqual(response.data["title"], self.task.title)

    def test_update_task(self):
        data = {"title": "Обновленное название"}
        response = self.client.patch(self.task_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Обновленное название")

    def test_delete_task(self):
        response = self.client.delete(self.task_url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_list_tasks(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)


class EmployeeAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test2@test.com", password="12345")
        self.employee = Employee.objects.create(full_name="Петр Петров", user=self.user)
        self.client = APIClient()
        self.client.login(email="test2@test.com", password="12345")
        self.employee_url = reverse("tracker:employee-detail", args=[self.employee.id])
        self.list_url = reverse("tracker:employee-list")

    def test_create_employee(self):
        new_user = User.objects.create_user(email="empl@mail.com", password="54321")
        data = {
            "full_name": "Анна Смирнова",
            "user": new_user.id,
            "position": "Developer",
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Employee.objects.count(), 2)

    def test_retrieve_employee(self):
        response = self.client.get(self.employee_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], self.employee.full_name)

    def test_update_employee(self):
        data = {"full_name": "Александр Новиков"}
        response = self.client.patch(self.employee_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "Александр Новиков")

    def test_delete_employee(self):
        response = self.client.delete(self.employee_url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Employee.objects.filter(id=self.employee.id).exists())

    def test_list_employees(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
