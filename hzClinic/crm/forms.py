from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import SelectDateWidget, Textarea, ModelForm, CheckboxSelectMultiple, DateInput, TextInput

from users.models import CustomUser

from crm.models import hzUserInfo, Candidate


class LoginForm(forms.Form):
    user_login = forms.CharField(label='', max_length=50)
    user_password = forms.CharField(label='', max_length=10, widget=forms.PasswordInput())

    user_login.widget.attrs.update({'class': 'input-material', 'placeholder': 'введите логин (79998887755)'})
    user_password.widget.attrs.update({'class': 'input-material', 'placeholder': 'введите пароль'})

class QuestForm(forms.Form):
    phone = forms.CharField(max_length=16, label='Номер телефона')
    FIO = forms.CharField(max_length=100, label='Ф.И.О.')
    DateOfB = forms.DateField(input_formats=['%d.%m.%Y', '%Y-%m-%d'], label='Дата рождения')
    AddressRow = forms.CharField(max_length=255, label='Адрес места жительства из анкеты')
    Address = forms.CharField(max_length=255, label='Адрес обработанный (будет использован в документах)')
    veSub = forms.CharField(max_length=100, label='Субъект (Республика/Край/Область)')
    veRn = forms.CharField(max_length=100, label='Район субъекта')
    veGor = forms.CharField(max_length=100, label='Город')
    veNP = forms.CharField(max_length=100, label='Населённый пункт')
    veUl = forms.CharField(max_length=100, label='Улица (без ул.)')
    veDom = forms.CharField(max_length=100, label='Номер дома')
    veStr = forms.CharField(max_length=100, label='Строение/Корпус/Владение и т.д.')
    veKv = forms.CharField(max_length=100, label='Квартира')
    PerZ = forms.CharField(max_length=100, label='Перенесённые и хронические заболевания?')
    PerO = forms.CharField(max_length=100, label='Перенесённые пластические операции')
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
    MedPrep = forms.CharField(max_length=100, label='Лекарственные препараты на постоянной основе')
    MedIzd = forms.CharField(max_length=100, label='Медицинские изделия')
    Gender = forms.CharField(max_length=100, label='Пол')
    oGender = forms.CharField(max_length=100, label='Дополнительная информация для осмотра, в зависимости от пола')
    Rost = forms.CharField(max_length=100, label='Рост, см')
    Massa = forms.CharField(max_length=100, label='Вес, кг')
    GK = forms.CharField(max_length=100, label='Группа крови (O(I), A(II), B(III), AB(IV))')
    RH = forms.CharField(max_length=100, label='Резус-фактор (+, -)')
    KELL = forms.CharField(max_length=100, label='Келл-фактор (отрицательный, положительный)')

    # class Meta:
    #     # model = hzUserInfo
    #     # exclude = ['hz_user', 'type', ]
    #     widgets = {'AddressRow': forms.Textarea,
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
                  'notes': 'Примечания (необязательное)',
                  }
        model = Candidate
        fields = ['date_oper', 'phoneNumber', 'Sname', 'Name', 'Mname', 'notes', 'typeOpers']
        widgets = {
            'typeOpers': CheckboxSelectMultiple(attrs={'class': 'form-control-label'}),
            'date_oper': TextInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phoneNumber': TextInput(attrs={'placeholder': 'формат ввода 79998887766', 'class': 'form-control', 'pattern': '^\+?1?\d{8,15}$'}),
            'Sname': TextInput(attrs={'help_text': 'help_text', 'placeholder': 'Фамилия', 'class': 'form-control'}),
            'Name': TextInput(attrs={'placeholder': 'Имя', 'class': 'form-control'}),
            'Mname': TextInput(attrs={'placeholder': 'Отчество', 'class': 'form-control'}),
            'notes': TextInput(attrs={'placeholder': 'Примечания', 'class': 'form-control'}),
        }

