from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse

from crm.models import hzUserInfo

from crm.forms import LoginForm, QuestForm


def main_view(request):
    template_name = 'crm/_base.html'
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
        print(reverse(main_view))
        return redirect(reverse(main_view))
    if request.method == 'POST':
        username = request.POST.get('user_login', None)
        password = request.POST.get('user_password', None)
        # print('username=', username)
        # print('password=', password)
        user = authenticate(username=username, password=password)
        print('user=', user)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(main_view)
            # else:
            #     pass
        else:
            return HttpResponse('Invalid login or passpword!')
    template_name = 'crm/login.html'
    form = LoginForm()
    context = {'form': form}
    return render(request, template_name=template_name, context=context)
    # context = {'title': 'login_title', 'main_body': 'WELCOMMEN!'}
    # return render(request, template_name, context=context)


def logout_view(request):
    logout(request)
    template_name = 'crm/main.html'
    context = {'title': 'logout_title', 'main_body': 'By-by!!!'}
    return render(request, template_name, context=context)


def questionnaire_view(request):
    template_name = 'crm/main.html'
    form = QuestForm()
    context = {'title': 'Анкета',
               'main_body': 'Заполните эту анкету',
               'form': form,
               }
    return render(request, template_name, context=context)
