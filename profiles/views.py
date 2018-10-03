from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import RedirectView
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

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)


class LogoutView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return reverse('home')


class AutoLoginView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if not settings.DEBUG:
            raise Exception("Available in debug mode only")
        user_id = self.kwargs.get('id')
        user = User.objects.get(pk=user_id)
        password = 'test12345678'
        user = authenticate(username=user.username, password=password)
        assert user
        login(self.request, user)
        return reverse('home')
