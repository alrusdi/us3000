from django import forms
from django.contrib.auth.models import User


def validate_username(username):
    # 1. strip
    # 2. lower
    # 3. check if contains letters, digits and underscore
    # 4. ValidatonError if check is incorrect
    return username


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
        # Валидация: username не более 30 символов, только нижний регистр, цифры и "_"

    def clean_password(self):
        password = self.cleaned_data["password"]
        # любой пароль, главное что бы password == password_confirm
        # trim (strip): всегда отчищаем от пробельных символов в начале и в конце
        return password


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data["username"]
        username_exists = User.objects.filter(username=username).exists()
        if not username_exists:
            raise forms.ValidationError("Такого пользователя не найдено")
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        # любой пароль, главное что бы password == password_confirm
        # trim (strip): всегда отчищаем от пробельных символов в начале и в конце
        return password
        # проверить правильнйы ли пароль