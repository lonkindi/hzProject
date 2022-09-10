from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import SelectDateWidget, Textarea

from users.models import CustomUser

from crm.models import hzUserInfo


class LoginForm(forms.Form):
    user_login = forms.CharField(label='', max_length=50)
    user_password = forms.CharField(label='', max_length=10, widget=forms.PasswordInput())

    user_login.widget.attrs.update({'class': 'input-material', 'placeholder': 'введите логин'})
    user_password.widget.attrs.update({'class': 'input-material', 'placeholder': 'введите пароль'})


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('username', 'email', 'is_staff')


class QuestForm(forms.ModelForm):
    class Meta:
        model = hzUserInfo
        exclude = ['hz_user', 'type', ]
        widgets = {'DOB': SelectDateWidget(),
                   #'reg_address': Textarea(),
                   }
