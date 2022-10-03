import datetime
import random
import re

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse

from crm.models import hzUserInfo, Anket, TypeOperations

from crm.forms import LoginForm, QuestForm


def date_plus(c_date, delta):
    new_date = c_date + datetime.timedelta(days=delta)
    res_date = new_date.strftime('%d.%m.%Y')
    return res_date


def do_docs(context_dict):
    
    select_operations = selected_operations
    
    docs_context = {'sDate0': '', 'FIO': '', 'sFIO': '', 'sOpers': '', 'DR': '', 'DG': '', 'Adr': '', 'Job': '',
                    'DateAZ': '', 'DateAN': '', 'DateSP': '', 'DateSV': '', 'Date0': '', 'Date1': '', 'Date2': '',
                    'Date3': '', 'Date5': '', 'Date6': '', 'Date7': '', 'Date14': '', 'Date15': '', 'Date29': '',
                    'DopBlef': '', 'PerZ': '', 'PerO': '', 'PerT': '', 'PerG': '', 'Allerg': '', 'Alk': '', 'Nark': '',
                    'Gepatit': '', 'Kur': '', 'CDD': '', 'CSS': '', 'AD': '', 'Temp': '', 'TempD': '', 'Risk': '',
                    'VICH': '', 'Tub': '', 'Tif': '', 'Diabet': '', 'Vener': '',
                    }

    select_date = selected_date.toPyDate()
    today = datetime.datetime.today().date()

    for item in [0, 1, 2, 3, 5, 6, 7, 14, 15, 29]:
        docs_context['Date' + str(item)] = date_plus(select_date, item)
    delta_ambul = -random.choice(range(3, 180, 1))
    
    docs_context['DateAZ'] = date_plus(select_date, delta_ambul)
    docs_context['DateAN'] = docs_context['DateAZ']
    docs_context['DateSP'] = docs_context['Date0']
    docs_context['DateSV'] = ''

    DopBlef = ''
    if ui.DopBlefEdit.text() != '':
        DopBlef = ', ' + ui.DopBlefEdit.text()
    docs_context['DopBlef'] = DopBlef

    docs_context['PerZ'] = ui.PerZEdit.text()
    docs_context['PerO'] = ui.PerOEdit.text()
    docs_context['PerT'] = ui.PerTEdit.text()
    docs_context['PerG'] = ui.PerGEdit.text()
    docs_context['Allerg'] = ui.AllergEdit.text()
    docs_context['Kur'] = ui.KurEdit.text()
    docs_context['Alk'] = ui.AlkEdit.text()
    docs_context['Nark'] = ui.NarkEdit.text()
    docs_context['Gepatit'] = ui.GepatitEdit.text()
    docs_context['Risk'] = ui.RiskEdit.text()
    docs_context['VICH'] = ui.VICHEdit.text()
    docs_context['Tub'] = ui.TubEdit.text()
    docs_context['Tif'] = 'отрицает'  # ui.TifEdit.text()
    docs_context['Diabet'] = ui.DiabetEdit.text()
    docs_context['Vener'] = ui.VenerEdit.text()

    docs_context['sDate0'] = re.sub('\D', '', docs_context['Date0'])
    docs_context['FIO'] = ui.FIOEdit.text()
    docs_context['sFIO'] = re.sub(r'\b(\w+)\b\s+\b(\w)\w*\b\s+\b(\w)\w*\b', r'\1\2\3', docs_context['FIO'])

    sum_opers = '-'
    for item in selected_operations:
        for oper in TEST_DATA.types_operations:
            if oper[1] == item:
                sum_opers += (oper[2] + '-')

    docs_context['sOpers'] = sum_opers[1:-1]
    docs_context['DR'] = ui.DREdit.text()
    docs_context['DG'] = ui.DREdit.text()[6:]
    docs_context['Adr'] = ui.AdrEdit.text()
    docs_context['Job'] = ui.JobEdit.text()

    docs_context['Temp'] = 36.0 + random.choice(range(3, 9, 1)) / 10
    docs_context['TempD'] = 36.0 + random.choice(range(5, 9, 1)) / 10
    docs_context['CDD'] = random.choice(range(16, 25, 1))
    docs_context['CSS'] = random.choice(range(64, 98, 1))
    docs_context['AD'] = str(random.choice(range(110, 135, 5))) + '/' + str(random.choice(range(70, 90, 5)))
    if len(selected_operations) == 0:
        print_status('Операции НЕ выбраны, документы НЕ будут сформированы!')
    else:
        print_status(
            'Документы сформированы и сохранены в папке: ' + fill_tmpl(selected_operations, docs_context))
        ext_id = ui.ext_ID.text()
        req_data = TEST_DATA.req_data
        req_login = requests.post('http://cr74664-django-l4m8f.tw1.ru/login', data=req_data)
        token = json.loads(req_login.text)['Token']
        headers = {'Authorization': 'Token ' + token}
        req_upd_anket = requests.put('http://cr74664-django-l4m8f.tw1.ru/putanket?id=' + ext_id + '&state=1',
                                     headers=headers)


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
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
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
        item_dict['FIO'] = item.content['Фамилия'] + ' ' + item.content['Имя'] + ' ' + item.content['Отчество']
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
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    # context = dict()
    if request.method == 'POST':
        form = QuestForm(request.POST)
        # do_docs(request.POST)
        print(request.POST)
        # print("FIO= " + str(form.cleaned_data.get("FIO")))
        if form.is_valid():
            first = form.cleaned_data.get("FIO")
            last = form.cleaned_data.get("DateOfB")
            email = form.cleaned_data.get("Address")
            print(form.cleaned_data.get("FIO"))
            return redirect(reverse(login_view))
    else:
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

        PerO = 'отрицает'
        PerOQ = anket_dict['У вас были операции раньше?']
        if PerOQ != 'Нет':
            PerO = anket_dict['Перечислите перенесённые операции']

        PerT = 'отрицает'
        PerTQ = anket_dict['У вас были травмы?']
        if PerTQ != 'Нет':
            PerT = anket_dict['Перечислите перенесённые ранее травмы']

        PerG = 'отрицает'
        PerGQ = anket_dict['Вы переносили гемотрансфузии?']
        if PerGQ != 'Нет':
            PerG = anket_dict['Перечислите перенесённые ранее гемотрансфузии']

        Allerg = 'отрицает'
        AllergQ = anket_dict['Были ли у Вас аллергические реакции?']
        if AllergQ != 'Нет':
            Allerg = anket_dict['На что были аллергические реакции?']

        VICH = 'отрицает'
        VICHQ = anket_dict['Являетесь ли Вы носителем ВИЧ-инфекции?']
        if VICHQ != 'Нет':
            VICH = 'ВИЧ-носитель'

        Gepatit = 'отрицает'
        GepatitQ = anket_dict['Болели ли вы гепатитом?']
        if GepatitQ != 'Нет':
            Gepatit = 'гепатит типа ' + anket_dict['Гепатитом какого типа вы болели?']

        Tub = 'отрицает'
        TubQ = anket_dict['Болели ли вы туберкулёзом лёгких?']
        if TubQ != 'Нет':
            Tub = 'положительно'

        Diabet = 'отрицает'
        DiabetQ = anket_dict['У вас есть сахарный диабет?']
        if DiabetQ != 'Нет':
            Diabet = anket_dict['Сахарный диабет какого типа и когда был диагностирован?']

        Vener = 'отрицает'
        VenerQ = anket_dict['Болели ли Вы венерическими заболеваниями?']
        if VenerQ != 'Нет':
            Vener = anket_dict['Какие венерические заболевания Вы перенесли?']

        Alk = anket_dict['Отношение к алкоголю']
        Kur = anket_dict['Отношение к курению']
        Nark = anket_dict['Отношение к наркотикам']

        initial = {'FIO': fio,
                   'DateOfB': res_date,
                   'Address': anket_dict['Адрес места жительства (регистрации)'],
                   'Job': anket_dict['Место работы, должность'],
                   'PerZ': PerZ,
                   'PerO': PerO,
                   'PerT': PerT,
                   'PerG': PerG,
                   'Allerg': Allerg,
                   'VICH': VICH,
                   'Gepatit': Gepatit,
                   'Tub': Tub,
                   'Diabet': Diabet,
                   'Vener': Vener,
                   'Alk': Alk,
                   'Kur': Kur,
                   'Nark': Nark,
                   }
        # for item in anket_dict.items():
        #     anket.append([item[0], item[1]])
        form = QuestForm(initial=initial)
    oper_types = TypeOperations.objects.all()

    context = {'title': 'Анкета',
               # 'anket': anket,
               'oper_types': oper_types,
               'form': form,
               'ext_id': ext_id,
               }
    # context['form'] = form
    template_name = 'crm/_quest.html'
    return render(request, template_name=template_name, context=context)
