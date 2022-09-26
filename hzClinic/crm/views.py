import datetime

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse

from crm.models import hzUserInfo, Anket

from crm.forms import LoginForm, QuestForm


def main_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    template_name = 'crm/_main.html'
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    # print(hzuser_info)
    type = hzuser_info[0].type
    type_lbl = hzuser_info[0].UserTypeChoices[type].label
    context = {'title': 'Главная страница',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'type_lbl': type_lbl,

               }
    return render(request, template_name=template_name, context=context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse(main_view))
    if request.method == 'POST':
        username = request.POST.get('user_login', None)
        password = request.POST.get('user_password', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(main_view)
            # else:
            #     pass
        else:
            return HttpResponse('Некорректный логин или пароль!')
    template_name = 'crm/login.html'
    form = LoginForm()
    context = {'form': form,
               'information': 'Для работы в системе необходимо авторизоваться',
               }
    return render(request, template_name=template_name, context=context)
    # context = {'title': 'login_title', 'main_body': 'WELCOMMEN!'}
    # return render(request, template_name, context=context)


def logout_view(request):
    logout(request)
    return redirect(reverse(login_view))
    # template_name = 'crm/login.html'
    # form = LoginForm()
    # context = {'form': form,
    #            'title': 'Вы покинули клинику',
    #            'information': 'Введите логин и пароль чтобы вернуться к работе',
    #            }
    # return render(request, template_name, context=context)


def quests_view(request):
    template_name = 'crm/_quests.html'
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    ankets = Anket.objects.filter()
    anket_list = list()
    for item in ankets:
        item_dict = dict()
        item_dict['state'] = item.state
        item_dict['external_id'] = item.external_id
        item_dict['date_filling'] = item.date_filling
        item_dict['FIO'] = item.content['Фамилия']+' '+item.content['Имя']+' '+item.content['Отчество']
        item_dict['DOB'] = item.content['Дата рождения']
        item_dict['tel'] = item.content['Ваш контактный телефон']
        item_dict['addr'] = item.content['Адрес места жительства (регистрации)']
        anket_list.append(item_dict)
    context = {'title': 'Анкеты',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'anket_list': anket_list,
               }
    return render(request, template_name=template_name, context=context)


def quest_view(request, ext_id):
    anket = list()
    anket_qs = Anket.objects.filter(external_id=ext_id)
    anket_dict = anket_qs[0].content

    fio = anket_dict['Фамилия'] + ' ' + anket_dict['Имя'] + ' ' + anket_dict['Отчество']
    res_date = datetime.datetime.strptime(anket_dict['Дата рождения'], "%Y-%m-%d").strftime('%d.%m.%Y')

    PerZ = 'ОРВИ'
    PerZQ = anket_dict['Перенесённые и хронические заболевания?']
    if PerZQ != 'Нет':
        PerZA = ', ' + anket_dict['Перечислите перенесённые и хронические заболевания']
        PerZ += PerZA


    initial = {'FIO': fio,
               'DateOfB': res_date,
               'Address': anket_dict['Адрес места жительства (регистрации)'],
               'Job': anket_dict['Место работы, должность'],
               'PerZ': PerZ,

               }
    # for item in anket_dict.items():
    #     anket.append([item[0], item[1]])
    form = QuestForm(initial=initial)

    template_name = 'crm/_quest.html'
    context = {'title': 'Анкета',
               'anket': anket,
               'form': form,
               }
    return render(request, template_name=template_name, context=context)
