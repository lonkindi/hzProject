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


def questionnaire_view(request):
    template_name = 'crm/_quests.html'
    form = QuestForm()
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    ankets = Anket.objects.filter()
    anket_list = list()
    for item in ankets:
        item_dict = dict()
        item_dict['state'] = item.state
        item_dict['external_id'] = item.external_id
        item_dict['date_filling'] = item.date_filling
        item_dict['FIO'] = item.content['Фамилия'] + item.content['Имя'] + item.content['Отчество']
        item_dict['DOB'] = item.content['Дата рождения']
        item_dict['tel'] = item.content['Ваш контактный телефон']
        item_dict['addr'] = item.content['Адрес места жительства (регистрации)']
        anket_list.append(item_dict)
    context = {'title': 'Анкета',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'form': form,
               'anket_list': anket_list,
               }
    return render(request, template_name=template_name, context=context)
