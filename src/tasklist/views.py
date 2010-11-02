# Create your views here.

from django import http

def index(request):
    return http.HttpResponse("<h1>Hello World</h1>")