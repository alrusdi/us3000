from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView


def hello_world(requst):
    return render(requst, 'words/hello_world.html')

class IndexView(TemplateView):
    template_name = "words/index.html"
