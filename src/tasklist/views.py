# Create your views here.

from django import http
from django import shortcuts
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from ext import template
from tasklist import models

@login_required
def index(request):
    return template.render(request, "tasklist/index.html", {
        'tasklists': models.TaskList.get_tasklists(request.user),
    })

@login_required
def add_list(request):
    if request.method == "POST":
        models.TaskList.objects.create(owner=request.user, name=request.POST.get("name", ""))
        return http.HttpResponseRedirect(reverse("tasklist:index"))
    raise http.Http404

@login_required
def add_task(request, tasklist_id):
    tasklist = shortcuts.get_object_or_404(models.TaskList, pk=tasklist_id)
    if request.method == "POST":
        models.Task.objects.create(tasklist=tasklist, description=request.POST.get("description", ""))
        return http.HttpResponseRedirect(tasklist.get_absolute_url())
    raise http.Http404

@login_required
def tasks(request, tasklist_id=None):
    tasklist = shortcuts.get_object_or_404(models.TaskList, pk=tasklist_id)
    return template.render(request, "tasklist/tasks.html", {
        'tasklist': tasklist,
        'tasks': models.Task.get_tasks(tasklist),
    })

@login_required
def toggle_status(request):
    task = shortcuts.get_object_or_404(models.Task, pk=request.POST.get("task"))
    task.toggle_status()
    task.save()
    return http.HttpResponse("success")

@login_required
def clear_completed(request):
    if request.method == "POST":
        tasklist = shortcuts.get_object_or_404(models.TaskList, pk=request.POST.get("tasklist_id"))
        tasklist.clear_completed()
        return http.HttpResponseRedirect(tasklist.get_absolute_url())
    raise http.Http404