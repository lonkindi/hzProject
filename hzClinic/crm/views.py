import datetime
import os
import random
import re
from docxtpl import DocxTemplate

from crm.forms import LoginForm, QuestForm
from crm.models import hzUserInfo, Anket, TypeOperations
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from crm import YaD

from hzClinic import settings, settings_local


# /home/dmitry/PycharmProjects/hzProject/hzClinic/crm/templates/crm/docs

def fill_tmpl(oper_list, context_dict):
    doc_folder = context_dict['sFIO'] + '_' + context_dict['sOpers'] + '_' + context_dict['sDate0']
    base_dir = settings.BASE_DIR
    file_path = os.path.join(base_dir, 'crm/templates/crm/docs/tmpls/')
    docs_path = os.path.join(base_dir, 'crm/templates/crm/docs/')
    target_path = docs_path + doc_folder
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    YaD.create_folder(f'MedicalCase/{doc_folder}')
    # else:
    #     os.mkdir(docs_path)
    # os.mkdir(docs_path + doc_folder)
    for item in oper_list:
        for type_doc in ['v', 'o', 'p', 's']:
            doc = DocxTemplate(file_path + type_doc + '_' + str(item.code) + '.docx')
            doc.render(context_dict)
            doc.save(
                docs_path + doc_folder + '/' + type_doc + '_' + str(item.code) + '_' + context_dict['sFIO'] + '.docx')
    doc = DocxTemplate(file_path + 'd.docx')
    doc.render(context_dict)
    doc.save(docs_path + doc_folder + '/d_' + context_dict['sFIO'] + '.docx')
    id_ext = int(context_dict.get('id_ext', 0))
    if id_ext:
        Anket.objects.filter(external_id=id_ext).update(state=1)

    for file in os.listdir(target_path):
        upload_file = target_path + '/' + file
        YaD.upload_file(upload_file, f'MedicalCase/{doc_folder}/{file}')

    return doc_folder

def date_plus(c_date, delta):
    new_date = c_date + datetime.timedelta(days=delta)
    res_date = new_date.strftime('%d.%m.%Y')
    return res_date


def do_docs(query_dict):
    
    selected_operations = []
    
    docs_context = {'id_ext': '', 'sDate0': '', 'FIO': '', 'sFIO': '', 'sOpers': '', 'DR': '', 'DG': '', 'Adr': '', 'Job': '',
                    'DateAZ': '', 'DateAN': '', 'DateSP': '', 'DateSV': '', 'Date0': '', 'Date1': '', 'Date2': '',
                    'Date3': '', 'Date5': '', 'Date6': '', 'Date7': '', 'Date14': '', 'Date15': '', 'Date29': '',
                    'DopBlef': '', 'PerZ': '', 'PerO': '', 'PerT': '', 'PerG': '', 'Allerg': '', 'Alk': '', 'Nark': '',
                    'Gepatit': '', 'Kur': '', 'CDD': '', 'CSS': '', 'AD': '', 'Temp': '', 'TempD': '', 'Risk': '',
                    'VICH': '', 'Tub': '', 'Tif': '', 'Diabet': '', 'Vener': '',
                    }
    oper_date_str = query_dict.get('operation_date', False)
    select_date = datetime.datetime.strptime(oper_date_str, "%Y-%m-%d")
    today = datetime.datetime.today().date()

    for item in [0, 1, 2, 3, 5, 6, 7, 14, 15, 29]:
        docs_context['Date' + str(item)] = date_plus(select_date, item)
    delta_ambul = -random.choice(range(3, 180, 1))
    
    docs_context['DateAZ'] = date_plus(select_date, delta_ambul)
    docs_context['DateAN'] = docs_context['DateAZ']
    docs_context['DateSP'] = docs_context['Date0']
    docs_context['DateSV'] = ''

    DopBlef = ''
    oper_dop1 = query_dict.get('oper_dop1', False)
    oper_dop2 = query_dict.get('oper_dop2', False)
    if oper_dop1:
        DopBlef += ', чик-лифт молярной клетчатки'
    if oper_dop2:
        DopBlef += ', липофилинг лица'
    docs_context['DopBlef'] = DopBlef

    docs_context['id_ext'] = query_dict.get('id_ext', False)
    docs_context['PerZ'] = query_dict.get('id_PerZ', False)
    docs_context['PerO'] = query_dict.get('id_PerO', False)
    docs_context['PerT'] = query_dict.get('id_PerT', False)
    docs_context['PerG'] = query_dict.get('id_PerG', False)
    docs_context['Allerg'] = query_dict.get('id_Allerg', False)
    docs_context['Kur'] = query_dict.get('id_Kur', False)
    docs_context['Alk'] = query_dict.get('id_Alk', False)
    docs_context['Nark'] = query_dict.get('id_Nark', False)
    docs_context['Gepatit'] = query_dict.get('id_Gepatit', False)
    docs_context['Risk'] = query_dict.get('id_Risk', False)
    docs_context['VICH'] = query_dict.get('id_VICH', False)
    docs_context['Tub'] = query_dict.get('id_Tub', False)
    docs_context['Tif'] = 'отрицает'  # ui.TifEdit.text()
    docs_context['Diabet'] = query_dict.get('id_Diabet', False)
    docs_context['Vener'] = query_dict.get('id_Vener', False)

    docs_context['sDate0'] = re.sub('\D', '', docs_context['Date0'])
    docs_context['FIO'] = query_dict.get('id_FIO', False)
    docs_context['sFIO'] = re.sub(r'\b(\w+)\b\s+\b(\w)\w*\b\s+\b(\w)\w*\b', r'\1\2\3', docs_context['FIO'])

    sum_opers = '-'
    # for item in selected_operations:
    for oper in TypeOperations.objects.all():
        oper_id = 'oper_' + str(oper.code)
        if query_dict.get(oper_id, False):
            selected_operations.append(oper)
            sum_opers += (oper.s_name + '-')

    docs_context['sOpers'] = sum_opers[1:-1]
    docs_context['DR'] = query_dict.get('id_DateOfB', False)
    docs_context['DG'] = docs_context['DR'][6:]
    docs_context['Adr'] = query_dict.get('id_Address', False)
    docs_context['Job'] = query_dict.get('id_Job', False)

    docs_context['Temp'] = 36.0 + random.choice(range(3, 9, 1)) / 10
    docs_context['TempD'] = 36.0 + random.choice(range(5, 9, 1)) / 10
    docs_context['CDD'] = random.choice(range(16, 25, 1))
    docs_context['CSS'] = random.choice(range(64, 98, 1))
    docs_context['AD'] = str(random.choice(range(110, 135, 5))) + '/' + str(random.choice(range(70, 90, 5)))
    # print(docs_context)
    # print(selected_operations)
    fill_tmpl(selected_operations, docs_context)


    # if len(selected_operations) == 0:
    #     print_status('Операции НЕ выбраны, документы НЕ будут сформированы!')
    # else:
    #     print_status(
    #         'Документы сформированы и сохранены в папке: ' + fill_tmpl(selected_operations, docs_context))
    #     ext_id = ui.ext_ID.text()
    #     req_data = TEST_DATA.req_data
    #     req_login = requests.post('http://cr74664-django-l4m8f.tw1.ru/login', data=req_data)
    #     token = json.loads(req_login.text)['Token']
    #     headers = {'Authorization': 'Token ' + token}
    #     req_upd_anket = requests.put('http://cr74664-django-l4m8f.tw1.ru/putanket?id=' + ext_id + '&state=1',
    #                                  headers=headers)


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


def quests_view(request, state_id=-1):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    template_name = 'crm/_quests.html'
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    stat_ankets = ' только лишь всех '
    if state_id == 0:
        stat_ankets = ' новых '
    elif state_id == 1:
        stat_ankets = ' оформленных '
    if state_id in (0, 1):
        ankets = Anket.objects.filter(state=state_id)
    else:
        ankets = Anket.objects.all()

    # ankets = Anket.objects.filter(state_filter)
    anket_list = list()
    for item in ankets:
        item_dict = dict()
        item_dict['state'] = item.state
        item_dict['external_id'] = item.external_id
        item_dict['date_filling'] = date_plus(item.date_filling, 0)
        item_dict['FIO'] = item.content['Фамилия'] + ' ' + item.content['Имя'] + ' ' + item.content['Отчество']
        item_dict['DOB'] =  datetime.datetime.strptime(item.content['Дата рождения'], "%Y-%m-%d").strftime('%d.%m.%Y')
        item_dict['tel'] = item.content['Ваш контактный телефон']
        item_dict['addr'] = item.content['Адрес места жительства (регистрации)']
        anket_list.append(item_dict)
    context = {'title': 'Анкеты',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'anket_list': anket_list,
               'stat_ankets': stat_ankets,
               }
    return render(request, template_name=template_name, context=context)


def quest_view(request, ext_id):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    # context = dict()
    if request.method == 'POST':
        do_docs(request.POST)
        return redirect(reverse(quests_view))
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

        form = QuestForm(initial=initial)
    oper_types = TypeOperations.objects.all()
    today = datetime.datetime.today().date().strftime("%Y-%m-%d")
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    context = {'title': 'Анкета',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'today': today,
               'oper_types': oper_types,
               'form': form,
               'ext_id': ext_id,
               'FIO': fio,
               'state': anket_qs[0].state,
               }
    template_name = 'crm/_quest.html'
    return render(request, template_name=template_name, context=context)
