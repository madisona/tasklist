from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tasklist.views',
    url('', 'index', name='index'),
)