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

class ListAppAuthenticatedTestCase(test.TestCase):
    def setUp(self):
        user = User(username="aaron", email="aaron@twomadisons.com")
        user.set_password("pswd")
        user.save()

        self.client = test.Client()
        self.client.login(username="aaron", password="pswd")

    def tearDown(self):
        self.client.logout()


class TaskListModelTests(test.TestCase):

    def should_use_name_as_string_representation(self):
        tasklist = models.TaskList(name="Aaron's Tasks")
        self.assertEqual(str(tasklist), tasklist.name)

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

    def should_get_absolute_url_to_task_list(self):
        tasklist = models.TaskList(pk=1)
        self.assertEqual(tasklist.get_absolute_url(), reverse("tasklist:tasks", kwargs={'tasklist_id': tasklist.pk}))


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

    def should_require_logged_in_user_for_index_page(self):
        client = test.Client()
        response = client.get(reverse("tasklist:index"))
        self.assertEqual(response.status_code, 302)

    def should_require_logged_in_user_for_add_list_page(self):
        client = test.Client()
        response = client.get(reverse("tasklist:add_list"))
        self.assertEqual(response.status_code, 302)

    def should_send_non_logged_in_user_to_login_page(self):
        client = test.Client()
        response = client.get(reverse("tasklist:index"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasklist/login.html")

class IndexPageTests(ListAppAuthenticatedTestCase):

    def should_allow_logged_in_user_to_access_page(self):
        response = self.client.get(reverse("tasklist:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasklist/index.html")        

    @patch("tasklist.models.TaskList.get_tasklists")
    def should_send_lists_to_template(self, query_mock):
        query_mock.return_value = []
        response = self.client.get(reverse("tasklist:index"))
        self.assertEqual(response.context['tasklists'], query_mock.return_value)

class AddListPageTests(ListAppAuthenticatedTestCase):

    def should_allow_logged_in_user_to_access_page(self):
        response = self.client.get(reverse("tasklist:add_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasklist/add_list.html")

    @patch('tasklist.forms.TaskListForm')
    def should_send_form_to_template(self, form_mock):
        form_mock.return_value.is_valid.return_value = False
        response = self.client.get(reverse("tasklist:add_list"))
        self.assertEqual(response.context['form'], form_mock.return_value)

    @patch('tasklist.forms.TaskListForm')
    def should_save_form_if_valid(self, form_mock):
        form_mock.return_value.is_valid.return_value = True

        response = self.client.get(reverse("tasklist:add_list"))
        self.assertTrue(form_mock.return_value.save.called, "Didn't call save on a valid form")

    @patch('tasklist.forms.TaskListForm')
    def should_redirect_to_index_page_if_valid_form(self, form_mock):
        form_mock.return_value.is_valid.return_value = True

        response = self.client.get(reverse("tasklist:add_list"))
        self.assertRedirects(response, reverse("tasklist:index"), status_code=302)

