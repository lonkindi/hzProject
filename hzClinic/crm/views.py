from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect

from crm.models import hzUserInfo

from crm.forms import LoginForm


def main_view(request):
    template_name = 'crm/index.html'
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    type = hzuser_info[0].type
    type_lbl = hzuser_info[0].UserTypeChoices[type].label
    # hzuser_type = hzuser_info[0].type
    # hzuser_foto = hzuser_info[0].hzuser_foto
    context = {'title': 'Главная страница',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'type_lbl':  type_lbl,
               }
    return render(request, template_name, context=context)


def login_view(request):
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
    template = 'crm/login.html'
    form = LoginForm()
    context = {'form': form}
    return render(request, template_name=template, context=context)
    # context = {'title': 'login_title', 'main_body': 'WELCOMMEN!'}
    # return render(request, template_name, context=context)


def logout_view(request):
    template_name = 'crm/main.html'
    context = {'title': 'logout_title', 'main_body': 'By-by!!!'}
    return render(request, template_name, context=context)
