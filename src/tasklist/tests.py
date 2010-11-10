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
        self.user = User(username="aaron", email="aaron@twomadisons.com")
        self.user.set_password("pswd")
        self.user.save()

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

    def should_get_absolute_url_to_add_task(self):
        tasklist = models.TaskList(pk=1)
        self.assertEqual(tasklist.get_add_task_url(), reverse("tasklist:add_task", kwargs={'tasklist_id': tasklist.pk}))


class TaskModelTests(test.TestCase):

    def should_use_description_as_string_representation(self):
        task = models.Task(description="New Task")
        self.assertEqual(str(task), "New Task")

    def should_default_status_to_zero(self):
        user = User.objects.create(username="aaron", password="pswd", email="a@b.com")
        tasklist = models.TaskList.objects.create(name="Aaron's Tasks", owner=user)
        task = models.Task.objects.create(tasklist=tasklist, description="New Task")
        self.assertEqual(task.status, 0)

    @patch("tasklist.models.Task.objects.filter")
    def should_get_non_deleted_tasks(self, query_mock):
        tasklist = Mock()
        tasks = models.Task.get_tasks(tasklist)
        self.assertEqual(query_mock.call_args, [(), {
            'tasklist': tasklist,
            'status__in': (0, 1),
        }])
        self.assertEqual(tasks, query_mock.return_value)

    def should_set_status_to_one_if_zero(self):
        task = models.Task(status=0)
        task.toggle_status()
        self.assertEqual(task.status, 1)

    def should_set_status_to_zero_if_one(self):
        task = models.Task(status=1)
        task.toggle_status()
        self.assertEqual(task.status, 0)

class AuthenticationTests(test.TestCase):

    def should_require_logged_in_user_for_index_page(self):
        client = test.Client()
        response = client.get(reverse("tasklist:index"))
        self.assertRedirects(response, reverse("login") + "?next=/", 302)

    def should_require_logged_in_user_for_add_list_page(self):
        client = test.Client()
        response = client.get(reverse("tasklist:add_list"))
        self.assertRedirects(response, reverse("login") + "?next=/add-list/", 302)

    def should_require_logged_in_user_for_tasks_page(self):
        client = test.Client()
        response = client.get(reverse("tasklist:tasks", args=(1,)))
        self.assertRedirects(response, reverse("login") + "?next=/tasks/1/", 302)

    def should_require_logged_in_user_for_add_task_page(self):
        client = test.Client()
        response = client.get(reverse("tasklist:add_task", args=(1,)))
        self.assertRedirects(response, reverse("login") + "?next=/add-task/1/", 302)

    def should_require_logged_in_user_for_toggle_status_page(self):
        client = test.Client()
        response = client.get(reverse("tasklist:toggle_status"))
        self.assertRedirects(response, reverse("login") + "?next=/toggle-status/", 302)

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

class TasksPage(ListAppAuthenticatedTestCase):

    @patch("tasklist.models.Task.get_tasks", Mock(return_value=[]))
    @patch("django.shortcuts.get_object_or_404", Mock(return_value=None))
    def should_allow_logged_in_user_to_access_tasks_page(self):
        response = self.client.get(reverse("tasklist:tasks", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasklist/tasks.html")

    def should_return_404_if_tasklist_not_found(self):
        response = self.client.get(reverse("tasklist:tasks", args=(1,)))
        self.assertEqual(response.status_code, 404)

    @patch("tasklist.models.Task.get_tasks")
    @patch("django.shortcuts.get_object_or_404")
    def should_send_tasks_and_tasklist_to_template(self, tasklist_mock, tasks_mock):
        tasks_mock.return_value = []
        response = self.client.get(reverse("tasklist:tasks", args=(1,)))
        self.assertEqual(tasklist_mock.call_args, [(models.TaskList,), {'pk': '1'}])
        self.assertEqual(tasks_mock.call_args, [(tasklist_mock.return_value,), {}])
        self.assertEqual(response.context['tasklist'], tasklist_mock.return_value)
        self.assertEqual(response.context['tasks'], tasks_mock.return_value)

class AddTaskPage(ListAppAuthenticatedTestCase):

    @patch("django.shortcuts.get_object_or_404", Mock(return_value=None))
    def should_return_404_if_not_post(self):
        response = self.client.get(reverse("tasklist:add_task", args=(1,)))
        self.assertEqual(response.status_code, 404)

    def should_add_task_to_db(self):
        tasklist = models.TaskList.objects.create(name="Aaron's Tasks", owner=self.user)
        response = self.client.post(reverse("tasklist:add_task", args=(tasklist.pk,)), {'description': "something"})

        task = models.Task.objects.get(pk=1)
        self.assertEqual(task.description, "something")
        self.assertRedirects(response, reverse("tasklist:tasks", args=(tasklist.pk,)), status_code=302)

class ToggleStatusPage(ListAppAuthenticatedTestCase):

    def should_return_404_if_task_not_found(self):
        response = self.client.post(reverse("tasklist:toggle_status"), {'task': "1"})
        self.assertEqual(response.status_code, 404)

    @patch("django.shortcuts.get_object_or_404")
    def should_toggle_status_and_save(self, get_mock):
        response = self.client.post(reverse("tasklist:toggle_status"), {'task': "1"})
        self.assertTrue(get_mock.return_value.toggle_status.called)
        self.assertTrue(get_mock.return_value.save.called)


#    task = shortcuts.get_object_or_404(models.Task, pk=request.POST.get("task"))
#    task.toggle_status()
#    task.save()



