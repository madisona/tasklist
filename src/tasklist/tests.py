"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from mock import patch, Mock
from django import test

from django.contrib.auth.models import User
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


class IndexPageTests(test.TestCase):

    @patch("tasklist.models.TaskList.get_tasklists")
    def should_send_lists_to_template(self, query_mock):
        pass
