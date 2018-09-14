from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def validate_username(username):
    # 1. strip
    username = username.strip()
    if len(username) > 30:
        raise ValidationError("Длина имени пользователя не"
                              " должна привышать 30 символов")
    # 2. lower
    username = username.lower()
    # 3. check if contains letters, digits and underscore
    permitted_signs = 'abcdefghijklmnopqrstuvwxyz1234567890_'
    for sign in username:
        if sign not in permitted_signs:
            raise ValidationError('Имя пользователя содержит недопустимые'
                                  ' символы. Пожайлуйста, используйте только'
                                  ' буквы латинского алфавита, цифры и знак '
                                  '"_"')
    # 4. ValidatonError if check is incorrect
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
        # Валидация: username не более 30 символов, только нижний регистр, цифры и "_"

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