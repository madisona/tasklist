from django.db import models

from django.contrib.auth.models import User

class TaskList(models.Model):
    ACTIVE = 0
    INACTIVE = 1

    STATUSES = (
        (ACTIVE, "active"),
        (INACTIVE, "inactive"),
    )

    owner = models.ForeignKey(User)
    name = models.CharField(max_length=20)
    status = models.IntegerField(default=ACTIVE, choices=STATUSES)
    creation_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def clear_completed(self):
        Task.objects.filter(tasklist=self, status=Task.COMPLETED).delete()

    @staticmethod
    def get_tasklists(user):
        return TaskList.objects.filter(owner=user, status=TaskList.ACTIVE)

    @models.permalink
    def get_absolute_url(self):
        return ("tasklist:tasks", None, {'tasklist_id': self.pk})

    @models.permalink
    def get_add_task_url(self):
        return ("tasklist:add_task", None, {'tasklist_id': self.pk})

class Task(models.Model):
    ACTIVE = 0
    COMPLETED = 1

    STATUSES = (
        (ACTIVE, "active"),
        (COMPLETED, "completed"),
    )

    tasklist = models.ForeignKey(TaskList)
    description = models.CharField(max_length=100)
    status = models.IntegerField(default=ACTIVE, choices=STATUSES)
    creation_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.description

    @staticmethod
    def get_tasks(tasklist):
        return Task.objects.filter(tasklist=tasklist)

    def toggle_status(self):
        self.status = self.COMPLETED if self.status == self.ACTIVE else self.ACTIVE

