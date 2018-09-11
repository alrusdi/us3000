from django import forms
from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(max_length=100, widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data["username"]
        username_exists = User.objects.filter(username=username).exists()
        if username_exists:
            raise forms.ValidationError("Пользователь с таким именем уже существует."
                                        " Пожалуйста, выберите другое имя")
        return username
