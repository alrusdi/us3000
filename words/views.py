from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


def hello_world(requst):
    return render(requst, 'words/hello_world.html')


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = "words/index.html"
