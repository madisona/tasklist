
from django import forms

from tasklist import models

class TaskListForm(forms.ModelForm):

    class Meta:
        model = models.TaskList
        fields = ("name", )