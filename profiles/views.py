from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic.edit import FormView
from profiles.forms import RegistrationForm, LoginForm


class RegistrationView(FormView):
    form_class = RegistrationForm
    template_name = 'profiles/registration.html'
    success_url = '/'

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = User.objects.create_user(username=username,
                                        email='{}@debugmail.io'.format(username),
                                        password=password)
        user = authenticate(username=username, password=password)
        assert user
        login(self.request, user)
        return super().form_valid(form)


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'profiles/login.html'
    success_url = '/'

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super().form_valid(form)
