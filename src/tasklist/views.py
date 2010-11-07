# Create your views here.

from django import http
from django import shortcuts
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from ext import template
from tasklist import models
from tasklist import forms

@login_required
def index(request):
    return template.render(request, "tasklist/index.html", {
        'tasklists': models.TaskList.get_tasklists(request.user),
    })

@login_required
def add_list(request):
    tasklist = models.TaskList(owner=request.user)
    form = forms.TaskListForm(request.POST or None, instance=tasklist)
    if form.is_valid():
        form.save()
        return http.HttpResponseRedirect(reverse("tasklist:index"))
        
    return template.render(request, "tasklist/add_list.html", {
        'form': form,
    })

#def add_task(request, list_id):
#    form = forms.AddTaskForm(request.POST or None)
#    if form.is_valid():
#        list = models.List.get_by_id(int(list_id))
#        form.save(list)
#        return http.HttpResponseRedirect(reverse('listapp:tasks', args=[list.key().id()]))
#    return template.render(request, "add_task.html", {
#        'form': form,
#    })
#


@login_required
def tasks(request, tasklist_id=None):
    tasklist = shortcuts.get_object_or_404(models.TaskList, pk=tasklist_id)
    return template.render(request, "tasklist/tasks.html", {
        'tasklist': tasklist,
        'tasks': models.Task.get_tasks(tasklist),
    })
#
#def change_status(request):
#    logging.warn("we're at the ajax test")
#    logging.warn("Task id: " + request.POST.get('task'))
#    task = models.Task.get_by_id(int(request.POST.get('task')))
#    if task.status == 'active':
#        task.status = "completed"
#    elif task.status == 'completed':
#        task.status = 'active'
#    task.put()
#    return http.HttpResponse("success!")