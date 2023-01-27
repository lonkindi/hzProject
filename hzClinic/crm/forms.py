from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import SelectDateWidget, Textarea, ModelForm, CheckboxSelectMultiple, DateInput, TextInput

from users.models import CustomUser

from crm.models import hzUserInfo, Candidate


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


class CandidateForm(ModelForm):
    error_css_class = 'has-danger'
    # required_css_class = 'has-warning'
    class Meta:
        error_messages = {'typeOpers': {'required': 'Не выбраны виды планируемых операций!'},
                          'phoneNumber': {'unique': 'Кандидат с таким номером телефона уже записан!'}
                          }
        labels = {'typeOpers': 'Операции (обязательное*)', 'date_oper': 'Дата операции (обязательное*)',
                  'phoneNumber': 'Номер телефона (обязательное*)', 'Sname': 'Фамилия (обязательное*)',
                  'Name': 'Имя (обязательное*)', 'Mname': 'Отчество (необязательное)',
                  }
        model = Candidate
        fields = ['date_oper', 'phoneNumber', 'Sname', 'Name', 'Mname', 'typeOpers']
        widgets = {
            'typeOpers': CheckboxSelectMultiple(attrs={'class': 'form-control-label'}),
            'date_oper': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phoneNumber': TextInput(attrs={'placeholder': 'формат ввода +79998887766', 'class': 'form-control', 'pattern': '^\+?1?\d{8,15}$'}),
            'Sname': TextInput(attrs={'help_text': 'help_text', 'placeholder': 'Фамилия', 'class': 'form-control'}),
            'Name': TextInput(attrs={'placeholder': 'Имя', 'class': 'form-control'}),
            'Mname': TextInput(attrs={'placeholder': 'Отчество', 'class': 'form-control'}),
        }

