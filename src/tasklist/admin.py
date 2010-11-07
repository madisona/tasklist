from django.contrib import admin
from tasklist import models

admin.site.register(models.TaskList)
admin.site.register(models.Task)