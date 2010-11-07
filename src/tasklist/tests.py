"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from mock import patch, Mock
from django import test

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from tasklist import models

class TaskListModelTests(test.TestCase):

    def should_use_name_as_string_representation(self):
        tasklist = models.TaskList(name="Aaron's Tasks")
        self.assertEqual(str(tasklist), "Aaron's Tasks")

    def should_default_status_to_zero(self):
        user = User.objects.create(username="aaron", password="pswd", email="a@b.com")
        tasklist = models.TaskList.objects.create(name="Aaron's Tasks", owner=user)
        self.assertEqual(tasklist.status, 0)

    @patch("tasklist.models.TaskList.objects")
    def should_get_all_lists(self, query_mock):
        user = Mock()
        tasklists = models.TaskList.get_tasklists(user)
        self.assertEqual(query_mock.method_calls, [("filter", (), {
            'owner': user,
            'status': 0,
        })])
        self.assertEqual(tasklists, query_mock.filter.return_value)


class TaskModelTests(test.TestCase):

    def should_use_description_as_string_representation(self):
        task = models.Task(description="New Task")
        self.assertEqual(str(task), "New Task")

    def should_default_status_to_zero(self):
        user = User.objects.create(username="aaron", password="pswd", email="a@b.com")
        tasklist = models.TaskList.objects.create(name="Aaron's Tasks", owner=user)
        task = models.Task.objects.create(tasklist=tasklist, description="New Task")
        self.assertEqual(task.status, 0)


class IndexPageAuthenticationTests(test.TestCase):

    def should_require_logged_in_user(self):
        client = test.Client()
        response = client.get(reverse("tasklist:index"))
        self.assertEqual(response.status_code, 302)

    def should_send_non_logged_in_user_to_login_page(self):
        client = test.Client()
        response = client.get(reverse("tasklist:index"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasklist/login.html")

class IndexPageTests(test.TestCase):

    def setUp(self):
        user = User(username="aaron", email="aaron@twomadisons.com", is_active=True)
        user.set_password("pswd")
        user.save()
        
        self.client = test.Client()
        rs = self.client.login(username="aaron", password="pswd")

    def tearDown(self):
        self.client.logout()

    def should_allow_logged_in_user_to_access_page(self):
        response = self.client.get(reverse("tasklist:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasklist/index.html")        

    @patch("tasklist.models.TaskList.get_tasklists")
    def should_send_lists_to_template(self, query_mock):
        response = self.client.get(reverse("tasklist:index"))
        self.assertEqual(response.context['tasklists'], query_mock.return_value)
