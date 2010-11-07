from django.db import models

from django.contrib.auth.models import User

class TaskList(models.Model):
    STATUSES = (
        (0, "active"),
        (1, "inactive"),
    )

    owner = models.ForeignKey(User)
    name = models.CharField(max_length=20)
    status = models.IntegerField(default=0, choices=STATUSES)
    creation_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def get_tasklists(user):
        return TaskList.objects.filter(owner=user, status=0)

    @models.permalink
    def get_absolute_url(self):
        return ("tasklist:tasks", None, {'tasklist_id': self.pk})

    @models.permalink
    def get_add_task_url(self):
        return ("tasklist:add_task", None, {'tasklist_id': self.pk})

class Task(models.Model):
    STATUSES = (
        (0, "active"),
        (1, "completed"),
        (2, "deleted"),
    )

    tasklist = models.ForeignKey(TaskList)
    description = models.CharField(max_length=100)
    status = models.IntegerField(default=0, choices=STATUSES)
    creation_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.description

    @staticmethod
    def get_tasks(tasklist):
        return Task.objects.filter(tasklist=tasklist, status__in=(0, 1))
