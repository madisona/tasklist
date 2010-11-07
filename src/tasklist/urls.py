from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tasklist.views',
    url('add-list', 'add_list', name='add_list'),
    url('', 'index', name='index'),
)