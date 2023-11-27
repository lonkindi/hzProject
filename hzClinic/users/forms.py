from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import SelectDateWidget, Textarea

#from users.models import CustomUser

from crm.models import hzUserInfo, Candidate

from users.models import CustomUser


class LoginForm(forms.Form):
    user_login = forms.CharField(label='', max_length=50)
    user_password = forms.CharField(label='', max_length=10, widget=forms.PasswordInput())

    user_login.widget.attrs.update({'class': 'input-material', 'placeholder': 'введите логин LoginForm'})
    user_password.widget.attrs.update({'class': 'input-material', 'placeholder': 'введите пароль LoginForm'})


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'phone', 'email', 'password')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('username', 'phone', 'email', 'is_staff')




class QuestForm(forms.Form):
    FIO = forms.CharField(max_length=100, label='Ф.И.О.')
    DateOfB = forms.DateField(input_formats=['%d.%m.%Y', '%Y-%m-%d'], label='Дата рождения')
    Address = forms.CharField(max_length=100, label='Адрес места жительства')
    Job = forms.CharField(max_length=255, label='Место работы, должность')
    PerZ = forms.CharField(max_length=100, label='Перенесённые и хронические заболевания?')
    PerO = forms.CharField(max_length=100, label='Перенесённые операции')
    PerT = forms.CharField(max_length=100, label='Перенесённые травмы')
    PerG = forms.CharField(max_length=100, label='Перенесённые гемотрансфузии')
    Allerg = forms.CharField(max_length=100, label='Аллергии')
    VICH = forms.CharField(max_length=100, label='ВИЧ')
    Gepatit = forms.CharField(max_length=100, label='Гепатит')
    Tub = forms.CharField(max_length=100, label='Туберкулёз')
    Diabet = forms.CharField(max_length=100, label='Диабет')
    Vener = forms.CharField(max_length=100, label='Венерические заболевания')
    Alk = forms.CharField(max_length=100, label='Отношение к алкоголю')
    Kur = forms.CharField(max_length=100, label='Отношение к курению')
    Nark = forms.CharField(max_length=100, label='Отношение к наркотикам')


    # class Meta:
    #     model = hzUserInfo
    #     exclude = ['hz_user', 'type', ]
    #     widgets = {'DOB': SelectDateWidget(),
    #                #'reg_address': Textarea(),
    #                }
