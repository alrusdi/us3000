from django.shortcuts import render
from django.views.generic.edit import FormView
from profiles.forms import RegistrationForm


class RegistrationView(FormView):
    form_class = RegistrationForm
    template_name = 'profiles/registration.html'
