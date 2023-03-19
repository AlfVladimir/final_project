from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase

from tmapp.models import Project, Sprint, Status, Task


class SigninTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpassword", email="test@testuser.com"
        )
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        user = authenticate(username="testuser", password="testpassword")
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_wrong_username(self):
        user = authenticate(username="wrong", password="testpassword")
        self.assertFalse(user is not None and user.is_authenticated)

    def test_wrong_pssword(self):
        user = authenticate(username="testuser", password="wrong")
        self.assertFalse(user is not None and user.is_authenticated)


class TaskTest(TestCase):
    def setUp(self):
        self.task = Task(
            name="Тестовое название",
            content="Тестовое описание",
        )

        self.task.save()

    def tearDown(self):
        self.task.delete()

    def test_read_task(self):
        self.assertEqual(self.task.name, "Тестовое название")
        self.assertEqual(self.task.content, "Тестовое описание")

    def test_update_task_description(self):
        self.task.content = "Измененное описание"
        self.task.save()
        self.assertEqual(self.task.content, "Измененное описание")


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project(
            name="Тестовое название",
            content="Тестовое описание",
        )

        self.project.save()

    def tearDown(self):
        self.project.delete()

    def test_read_project(self):
        self.assertEqual(self.project.name, "Тестовое название")
        self.assertEqual(self.project.content, "Тестовое описание")

    def test_update_project_description(self):
        self.project.content = "Измененное описание"
        self.project.save()
        self.assertEqual(self.project.content, "Измененное описание")

    def test_update_project_timestamp_done(self):
        self.project.is_complete = True
        self.project.save()
        self.assertEqual(self.project.timestamp_done is not False, True)


class AllTasksViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test", password="12test12", email="test@example.com"
        )
        self.user.save()
        self.client.login(username="test", password="12test12")

    def tearDown(self):
        self.user.delete()

    def test_no_tasks(self):
        response = self.client.get("/api/task/")
        self.assertEqual(response.data["results"], [])

    def test_one_task(self):
        self.task = Task(
            name="Тестовое название",
            content="Тестовое описание",
        )
        self.task.save()
        response = self.client.get("/api/task/")
        self.assertEqual(response.data["results"][0]["name"], "Тестовое название")
