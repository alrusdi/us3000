import re

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password


def validate_username(username):
    errors_list = []
    username = username.strip()
    if len(username) > 30:
        errors_list.append(
            ValidationError(
                "Длина имени пользователя не должна привышать 30 символов",
                code="username_too_long"
            )
        )
    username = username.lower()
    if not re.match(r'^[a-z0-9_]+$', username):
        errors_list.append(
            ValidationError(
                'Имя пользователя содержит недопустимые символы. Пожайлуйста,'
                ' используйте только буквы латинского алфавита, цифры и знак "_"',
                code='contains_wrong_characters'
            )
        )
    if errors_list:
        raise ValidationError(errors_list)
    return username


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(max_length=100, widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data["username"]
        validated_username = validate_username(username)
        username_exists = User.objects.filter(username=validated_username).exists()
        if username_exists:
            raise forms.ValidationError("Пользователь с таким именем уже существует."
                                        " Пожалуйста, выберите другое имя")
        return validated_username

    def clean_password(self):
        password = self.cleaned_data["password"]
        password = password.strip()
        return password

    def clean_password_confirm(self):
        password = self.cleaned_data["password"]
        password_confirm = self.cleaned_data["password_confirm"]
        password_confirm = password_confirm.strip()
        if password_confirm != password:
            raise forms.ValidationError("Пароль и подтверждение пароля не совпадают")
        return password_confirm


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data["username"]
        validated_username = validate_username(username)

        username_exists = User.objects.filter(username=validated_username).exists()
        if not username_exists:
            raise forms.ValidationError("Пользователь с таким именем не найден")
        return validated_username

    def clean_password(self):
        username = self.cleaned_data.get("username")
        if username is None:
            return
        password = self.cleaned_data["password"]
        password = password.strip()
        password_hash_in_db = User.objects.filter(username=username).values()[0]['password']
        if not check_password(password, password_hash_in_db):
            raise forms.ValidationError("Некорректный пароль")
        return password
