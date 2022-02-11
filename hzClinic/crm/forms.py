from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from users.models import CustomUser


class LoginForm(forms.Form):
    user_login = forms.CharField(label='', max_length=50)
    user_password = forms.CharField(label='', max_length=10, widget=forms.PasswordInput())

    user_login.widget.attrs.update({'class': 'input-material', 'title': 'Your name'})
    user_password.widget.attrs.update({'class': 'input-material'})


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('username', 'email', 'is_staff')
