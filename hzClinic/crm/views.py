import ast
import datetime
import os
import random
import re
import csv
from dadata import Dadata

import requests
from django.core.paginator import Paginator
from docxtpl import DocxTemplate

from transliterate import translit
from crm.forms import LoginForm, QuestForm, CandidateForm, UploadForm
from crm.models import hzUserInfo, Anket, TypeOperations, Candidate
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from crm import YaD, MyAPI

from hzClinic import settings, settings_local


# class CandidateHTMxTableView(SingleTableMixin, FilterView):
#     table_class = CandidateHTMxTable
#     queryset = Candidate.objects.all()
#     filterset_class = CandidateFilter
#     paginate_by = 15
#
#     def get_template_names(self):
#         print(self.request)
#         if self.request.htmx:
#             template_name = "crm/candidate_table_partial.html"
#         else:
#             template_name = "crm/candidate_table_htmx.html"
#
#         return template_name

def page_not_found_view(request, exception):
    return render(request, 'crm/404.html', status=404)

def fill_tmpl(oper_list, context_dict):
    sFIO = translit(context_dict['sFIO'], 'ru', reversed=True)
    sOpers = translit(context_dict['sOpers'], 'ru', reversed=True)
    doc_folder = sFIO + '_' + sOpers + '_' + context_dict['sDate0']
    base_dir = settings.BASE_DIR
    file_path = os.path.join(base_dir, 'crm/docs/tmpls/')
    docs_path = os.path.join(base_dir, 'crm/docs/')
    target_path = docs_path + doc_folder

    if not os.path.exists(target_path):
        os.mkdir(target_path)

    for item in oper_list:
        doc = DocxTemplate(file_path + 's_' + str(item.code) + '.docx')
        doc.render(context_dict)
        target_str = target_path + '/' + 's_' + str(item.code) + '_' + sFIO + '.docx'
        doc.save(target_str)
    items = ['ids', 'fv', 'ln', 'oh', 'pe', 'po', 've', 'otkaz', 'svod', 'memo', 'napr', 'VTEO']
    if context_dict['scheme1']:
        items.append('schemeG')
    if context_dict['scheme2']:
        items.append('schemeT')
    for item in items:
        doc = DocxTemplate(file_path + item + '.docx')
        doc.render(context_dict)
        doc.save(docs_path + doc_folder + '/' + item + '_' + sFIO + '.docx')

    id_ext = int(context_dict.get('id_ext', 0))
    # if id_ext:
    #     MyAPI.update_anket_myapi(ext_id=id_ext, state=1)
    #
    # YaD.create_folder(f'MedicalCase/{doc_folder}')
    # for file in os.listdir(target_path):
    #     upload_file = target_path + '/' + file
    #     YaD.upload_file(upload_file, f'MedicalCase/{doc_folder}/{file}')

    return doc_folder

def send_telegram(text: str):
    token = settings_local.botTOKEN
    url = "https://api.telegram.org/bot"
    channel_id = "360620990"
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
         "chat_id": channel_id,
         "text": text
          })

    if r.status_code != 200:
        print(r.text)
        raise Exception("post_text error")



def date_plus(c_date, delta):
    new_date = c_date + datetime.timedelta(days=delta)
    res_date = new_date.strftime('%d.%m.%Y')
    return res_date


def del_duplicates(original_str, spliter=';'):
    original_lst = list(original_str.split(spliter))
    strip_list = list()
    for item in original_lst:
        if item != '':
            strip_list.append(str(item).strip())
    mod_list = list(dict.fromkeys(strip_list))
    rez_str = spliter.join(mod_list)
    rez_str = rez_str.replace(spliter, spliter+' ')
    return rez_str


def do_docs(query_dict):
    selected_operations = []
    docs_context = dict()
    oper_date_str = query_dict.get('operation_date', False)
    select_date = datetime.datetime.strptime(oper_date_str, "%Y-%m-%d")
    today = datetime.datetime.today().date()
    day_list = [0, 1, 2, 3, 5, 6, 7, 14, 15, 29]
    for item in day_list:
        docs_context['Date' + str(item)] = date_plus(select_date, item)
    docs_context['Nakanune'] = date_plus(select_date, -1)
    delta_ambul = -random.choice(range(3, 30, 1))

    docs_context['DateAZ'] = date_plus(select_date, delta_ambul)
    docs_context['DateAN'] = docs_context['DateAZ']
    docs_context['DateSP'] = docs_context['Date0']
    docs_context['DateSV'] = ''

    anest = ''
    anest1 = query_dict.get('anest1', False)
    anest2 = query_dict.get('anest2', False)
    anest3 = query_dict.get('anest3', False)
    anest4 = query_dict.get('anest4', False)

    if anest1:
        anest = 'общая ингаляционная анестезия'
        if anest2 and anest1:
            anest += ' + ИВЛ'
    if anest3 and anest:
        anest += ', местная анестезия'
    elif anest3 and not anest:
        anest = 'местная анестезия'
    if anest4 and anest3 and not anest1:
        anest += ' + мониторинг'
    docs_context['anest'] = anest

    docs_context['scheme1'] = query_dict.get('scheme1', False)
    docs_context['scheme2'] = query_dict.get('scheme2', False)

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
    docs_context['Diabet'] = query_dict.get('id_Diabet', False)
    docs_context['Vener'] = query_dict.get('id_Vener', False)

    docs_context['sDate0'] = re.sub('\D', '', docs_context['Date0'])
    docs_context['FIO'] = query_dict.get('id_FIO', False)
    docs_context['sFIO'] = re.sub(r'\b(\w+)\b\s+\b(\w)\w*\b\s+\b(\w)\w*\b', r'\1\2\3', docs_context['FIO'])
    docs_context['IO'] = re.sub(r'\b(\w+)\b\s+\b(\w*)\w*\b\s+\b(\w*)\w*\b', r'\2 \3', docs_context['FIO'])

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
    docs_context['Gender'] = query_dict.get('id_Gender', False)
    docs_context['oGender'] = query_dict.get('id_oGender', False)
    docs_context['MedPrep'] = query_dict.get('id_MedPrep', False)
    docs_context['MedIzd'] = query_dict.get('id_MedIzd', False)
    docs_context['veSub'] = query_dict.get('id_veSub', False)
    docs_context['veRn'] = query_dict.get('id_veRn', False)
    docs_context['veGor'] = query_dict.get('id_veGor', False)
    docs_context['veNP'] = query_dict.get('id_veNP', False)
    docs_context['veUl'] = query_dict.get('id_veUl', False)
    docs_context['veDom'] = query_dict.get('id_veDom', False)
    docs_context['veStr'] = query_dict.get('id_veStr', False)
    docs_context['veKv'] = query_dict.get('id_veKv', False)
    docs_context['Rost'] = query_dict.get('id_Rost', False)
    docs_context['Massa'] = query_dict.get('id_Massa', False)
    docs_context['GK'] = query_dict.get('id_GK', False)
    docs_context['RH'] = query_dict.get('id_RH', False)
    docs_context['KELL'] = query_dict.get('id_KELL', False)
    oHH = str(random.choice(range(9, 11, 1)))
    if len(oHH) == 1:
        oHH = '0' + oHH
    docs_context['oHH'] = oHH
    oMM = str(random.choice(range(0, 55, 5)))
    if len(oMM) == 1:
        oMM = '0' + oMM
    docs_context['oMM'] = oMM
    docs_context['oTemp'] = 36.0 + random.choice(range(3, 9, 1)) / 10
    docs_context['oCDD'] = random.choice(range(16, 20, 1))
    docs_context['oCSS'] = random.choice(range(64, 98, 1))
    docs_context['oSat'] = random.choice(range(98, 101, 1))
    docs_context['oAD'] = str(random.choice(range(110, 135, 5))) + '/' + str(random.choice(range(70, 90, 5)))
    docs_context['peTemp'] = 36.0 + random.choice(range(5, 9, 1)) / 10
    docs_context['peCDD'] = random.choice(range(16, 20, 1))
    docs_context['peCSS'] = random.choice(range(64, 98, 1))
    docs_context['peSat'] = random.choice(range(98, 101, 1))
    docs_context['peAD'] = str(random.choice(range(110, 135, 5))) + '/' + str(random.choice(range(70, 90, 5)))

    zaloby = ''
    pri_osmotre = ''
    osn_zabol = ''
    MKB = ''
    plan_lech = ''
    obosnov = ''
    naimen_oper = ''
    kod_usl = ''
    plan_oper = ''
    opis_oper = ''
    kol_instr = 0
    kol_salf = 0
    krovop = 0
    naznach = ''
    naznach_set = set()
    primen_lec = ''
    primen_lec_set = set()
    rezult = ''
    srok_gosp = 0

    for operation in selected_operations:
        curr_operation = TypeOperations.objects.filter(code=operation.code)[0]
        if zaloby == '':
            selector = ''
        else:
            selector = ';'
        zaloby += selector + curr_operation.zaloby

        if pri_osmotre == '':
            selector = ''
        else:
            selector = ';'
        pri_osmotre += selector + curr_operation.pri_osmotre

        if osn_zabol == '':
            selector = ''
        else:
            selector = ';'
        osn_zabol += selector + curr_operation.osn_zabol

        if MKB == '':
            selector = ''
        else:
            selector = ';'
        MKB += selector + curr_operation.MKB

        if plan_lech == '':
            selector = ''
        else:
            selector = ';'
        plan_lech += selector + curr_operation.plan_lech

        if obosnov == '':
            selector = ''
        else:
            selector = ';'
        obosnov += selector + curr_operation.obosnov

        if naimen_oper == '':
            selector = ''
        else:
            selector = ';'
        naimen_oper += selector + curr_operation.naimen_oper

        if kod_usl == '':
            selector = ''
        else:
            selector = ';'
        kod_usl += selector + curr_operation.kod_usl

        if plan_oper == '':
            selector = ''
        else:
            selector = ';\r\n'
        plan_oper += selector + curr_operation.plan_oper

        if opis_oper == '':
            selector = ''
        else:
            selector = '.\r\n'
        opis_oper += selector + curr_operation.opis_oper

        kol_instr += curr_operation.kol_instr
        kol_salf += curr_operation.kol_salf
        krovop += curr_operation.krovop

        if naznach == '':
            selector = ''
        else:
            selector = ','
        naznach += selector + curr_operation.naznach

        if primen_lec == '':
            selector = ''
        else:
            selector = ';'
        primen_lec += selector + curr_operation.primen_lec

        if rezult == '':
            selector = ''
        else:
            selector = ';'
        rezult += selector + curr_operation.rezult

        if curr_operation.srok_gosp > srok_gosp:
            srok_gosp = curr_operation.srok_gosp

    docs_context['zaloby'] = del_duplicates(zaloby)
    docs_context['pri_osmotre'] = del_duplicates(pri_osmotre)
    docs_context['osn_zabol'] = del_duplicates(osn_zabol)
    docs_context['MKB'] = del_duplicates(MKB)
    docs_context['plan_lech'] = del_duplicates(plan_lech)
    docs_context['obosnov'] = del_duplicates(obosnov)
    docs_context['naimen_oper'] = del_duplicates(naimen_oper)
    docs_context['kod_usl'] = del_duplicates(kod_usl)
    docs_context['plan_oper'] = plan_oper
    docs_context['opis_oper'] = opis_oper
    docs_context['kol_instr'] = kol_instr
    docs_context['kol_salf'] = kol_salf
    docs_context['krovop'] = krovop
    docs_context['naznach'] = del_duplicates(naznach, ',')
    primen_lec = del_duplicates(primen_lec, ';')
    for item in day_list:
        primen_lec_str = primen_lec.replace(f'{"{Date"+str(item)+"}"}', docs_context['Date' + str(item)])
        primen_lec = primen_lec_str
    docs_context['primen_lec'] = primen_lec#[:-1] #.replace(';', '; ')
    for i in range(1, 5):
        docs_context['ln_lp' + str(i)] = '\r\n\r\n\r\n'
    for index, value in enumerate(primen_lec.split(';')):
        ln_lp = re.search(r'(.*?) с ', value)
        ln_Date_n = re.search(r'с (\d\d.\d\d.*?) г.', value)
        ln_Date_o = re.search(r'по (\d\d.\d\d.*?) г.', value)
        docs_context['ln_lp' + str(index+1)] = ln_lp.group(1) if ln_lp else '\r\n\r\n\r\n'
        docs_context['ln_Date' + str(index+1) + '_n'] = ln_Date_n.group(1)+' г.\r\n\r\n_____________' if ln_Date_n else ''
        docs_context['ln_Date' + str(index+1) + '_o'] = ln_Date_o.group(1)+' г.\r\n\r\n_____________' if ln_Date_o else ''

    docs_context['rezult'] = del_duplicates(rezult)
    propis = {1: 'одни', 2: 'двое', 3: 'трое', 4: 'четверо', 5: 'пятеро', 6: 'шестеро', 7: 'семеро', 8: 'восемь', }
    if srok_gosp == 1:
        sutok = ' сутки'
    else:
        sutok = ' суток'
    docs_context['srok_gosp'] = str(srok_gosp) + f' ({propis.get(srok_gosp, False)}) ' + sutok
    docs_context['PZK'] = query_dict.get('PZK', False)

    fill_tmpl(selected_operations, docs_context)
    # print(f'selected_operations = {selected_operations}, docs_context = {docs_context}')
    # send_telegram('Hello BOT!')

def main_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    template_name = 'crm/_main.html'
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    type = hzuser_info[0].type
    type_lbl = hzuser_info[0].UserTypeChoices[type].label
    analizes_list = list()
    files_list = list()
    analizes = MyAPI.get_analyzes_myapi('79200228333')
    for item_row in analizes:
        item_raw = item_row.replace("'", '`')
        item = ast.literal_eval(item_raw.replace('"', "'") + '}')
        item_dict = dict()
        item_dict['state'] = item['state']
        item_dict['external_id'] = item['external_id']
        item_dict['date_filling'] = datetime.datetime.strptime(item['date_filling'], "%Y-%m-%d").strftime(
            '%d.%m.%Y')
        item_dict['FIO'] = item['f'] + ' ' + item['i'] + ' ' + item['o']
        item_dict['date_oper'] = datetime.datetime.strptime(item['date_oper'], "%Y-%m-%d").strftime(
            '%d.%m.%Y')
        item_dict['phone'] = item['phone']
        files_list = item['files'].split(',')
        item_file_list = list()
        for item_file in files_list:
            item_file_list.append([item_file[item_file.find('_')+1:], item_file])
        item_dict['files'] = item_file_list
        analizes_list.append(item_dict)

    context = {'title': 'Главная страница',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'type_lbl': type_lbl,
               'analizes': analizes_list,
               }
    return render(request, template_name=template_name, context=context)


def analyzes_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    template_name = 'crm/_analyzes.html'
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    type = hzuser_info[0].type
    type_lbl = hzuser_info[0].UserTypeChoices[type].label
    analizes_list = list()
    files_list = list()
    analizes = MyAPI.get_analyzes_myapi('0')
    for item_row in analizes:
        item_raw = item_row.replace("'", '`')
        item = ast.literal_eval(item_raw.replace('"', "'") + '}')
        item_dict = dict()
        item_dict['state'] = item['state']
        item_dict['external_id'] = item['external_id']
        item_dict['date_filling'] = datetime.datetime.strptime(item['date_filling'], "%Y-%m-%d").strftime(
            '%d.%m.%Y')
        item_dict['FIO'] = item['f'] + ' ' + item['i'] + ' ' + item['o']
        item_dict['date_oper'] = datetime.datetime.strptime(item['date_oper'], "%Y-%m-%d").strftime(
            '%d.%m.%Y')
        item_dict['phone'] = item['phone']
        files_list = item['files'].split(',')
        item_file_list = list()
        for item_file in files_list:
            item_file_list.append([item_file[item_file.find('_') + 1:], item_file])
        item_dict['files'] = item_file_list
        analizes_list.append(item_dict)
    paginator = Paginator(analizes_list, 12)
    current_page = request.GET.get('page', 1)
    b_analyzes = paginator.get_page(current_page)
    e_analyzes = paginator.get_elided_page_range(current_page, on_each_side=2, on_ends=1)
    if b_analyzes.has_previous():
        prev_page = b_analyzes.previous_page_number
        prev_page = prev_page()
    else:
        prev_page = 1
    if b_analyzes.has_next():
        next_page = b_analyzes.next_page_number
        next_page = next_page()
    else:
        next_page = paginator.num_pages
    context = {'title': 'Главная страница',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'type_lbl': type_lbl,
               'analyzes': b_analyzes,
               'e_analyzes': e_analyzes,
               'current_page': int(current_page),
               'prev_page_url': f'{reverse("analyzes")}?page={prev_page}',
               'next_page_url': f'{reverse("analyzes")}?page={next_page}',
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


def quests_view(request, state_id=9):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    template_name = 'crm/_quests.html'
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    ankets = []
    stat_ankets = 'Список только лишь всех анкет'
    if state_id == 0:
        stat_ankets = 'Список новых анкет'
    elif state_id == 1:
        stat_ankets = 'Список оформленных анкет'
    if state_id in (0, 1):
        ankets = MyAPI.get_ankets_myapi(state_id)
        # ankets = Anket.objects.filter(state=state_id)
    else:
        ankets = MyAPI.get_ankets_myapi(-1)
        # ankets = Anket.objects.all()
    # ankets = Anket.objects.filter(state_filter)
    anket_list = list()
    b_ankets = ''
    e_ankets = ''
    current_page = ''
    prev_page = ''
    next_page = ''
    current_page = 1

    if ankets != ['']:
        for item_row in ankets:
            item_raw = item_row.replace("'", '`')
            item = ast.literal_eval(item_raw.replace('"', "'") + '}')
            item_dict = dict()
            """ для анкет из БД
            item_dict['state'] = item.state
            item_dict['external_id'] = item.external_id
            item_dict['date_filling'] = item.date_filling
            item_dict['FIO'] = item.content['Фамилия'] + ' ' + item.content['Имя'] + ' ' + item.content['Отчество']
            item_dict['DOB'] = item.content['Дата рождения']
            item_dict['tel'] = item.content['Ваш контактный телефон']
            item_dict['addr'] = item.content['Адрес места жительства (регистрации)']
            """
            """для анкет из API"""
            item_dict['state'] = item['state']
            item_dict['external_id'] = item['external_id']
            item_dict['date_filling'] = datetime.datetime.strptime(item['date_filling'], "%Y-%m-%d").strftime(
                '%d.%m.%Y')
            item_dict['FIO'] = item['content']['Фамилия'] + ' ' + item['content']['Имя'] + ' ' + item['content'][
                'Отчество']
            item_dict['DOB'] = datetime.datetime.strptime(item['content']['Дата рождения'], "%Y-%m-%d").strftime(
                '%d.%m.%Y')
            item_dict['tel'] = item['content']['Ваш контактный телефон']
            # item_dict['addr'] = item['content']['Адрес места жительства (регистрации)']
            anket_list.append(item_dict)
        anket_list.sort(key=lambda anket: anket['FIO'])
        paginator = Paginator(anket_list, 12)
        current_page = request.GET.get('page', 1)
        b_ankets = paginator.get_page(current_page)
        e_ankets = paginator.get_elided_page_range(current_page, on_each_side=1, on_ends=1)
        # print('anket_list = ', anket_list)
        # print('sorted anket_list = ', sorted(anket_list, key=lambda anket: anket['FIO']))
        # prev_page, next_page = None, None
        if b_ankets.has_previous():
            prev_page = b_ankets.previous_page_number
            prev_page = prev_page()
        else:
            prev_page = 1
        if b_ankets.has_next():
            next_page = b_ankets.next_page_number
            next_page = next_page()
        else:
            next_page = paginator.num_pages
            # return render(request, template_name='index_bus.html', context={

            # })

    else:
        stat_ankets += ' пуст'
    context = {'title': 'Анкеты',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'stat_ankets': stat_ankets,
               'state_id': state_id,
               'anket_list': b_ankets, #anket_list,
               'e_ankets': e_ankets,
               'f_ankets': e_ankets,
               'current_page': int(current_page),
               'prev_page_url': f'{reverse("quests", args=[state_id])}?page={prev_page}',
               'next_page_url': f'{reverse("quests", args=[state_id])}?page={next_page}',
               }
    return render(request, template_name=template_name, context=context)


def quest_view(request, ext_id):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    # context = dict()
    if request.method == 'POST':
        do_docs(request.POST)
        return redirect(reverse('quests', args=[0]))
    else:
        anket = MyAPI.get_anket_myapi(ext_id) # list
        anket_str = anket[0].replace("'", '`')
        anket_qs = ast.literal_eval(anket_str.replace('"', "'") + '}')
        anket_dict = anket_qs['content']  # anket[0].content
        f = anket_dict.get('Фамилия', 'НЕТ')
        i = anket_dict.get('Имя', 'НЕТ')
        o = anket_dict.get('Отчество', '')
        fio = f + ' ' + i + ' ' + o
        raw_phone = anket_dict.get('Ваш контактный телефон', '')
        phone = re.sub('[\D]+','', raw_phone)
        AddressRow = anket_dict['Адрес места жительства (регистрации)']
        token = settings_local.DaDaAPI
        secret = settings_local.DaDaSecret
        dadata = Dadata(token, secret)
        result = dadata.clean("address", AddressRow)
        # print(result)
        Address = result['result']

        if Address:
            veSub = (result['region_type_full'] + ' ' + result['region']) if result['region_type_full'] == 'республика' else (result['region'] + ' ' + result['region_type_full'])
            veRn = result['area'] if result['area'] else ' - '
            veGor = result['city'] if result['city'] else ' - '
            veNP = (result['settlement_type_full'] + ' ' + result['settlement']) if result['settlement'] else ' - '
            if result['street']:
                veUl = (result['street_type_full'] + ' ' + result['street']) if result['street_type_full'] != 'улица' else result['street']
            else:
                veUl = '-'
            veDom = result['house'] if result['house'] else ' - '
            veStr = result['block'] if result['block'] else ' - '
            veKv = result['flat'] if result['flat'] else ' - '
        else:
            Address = veSub = veRn = veGor = veNP = veUl = veDom = veStr = veKv = 'не удалось определить'

        res_date = datetime.datetime.strptime(anket_dict['Дата рождения'], "%Y-%m-%d").strftime('%d.%m.%Y')

        PerZ = 'ОРВИ'
        PerZQ = anket_dict.get('Перенесённые и хронические заболевания?', 'Нет')
        if PerZQ != 'Нет':
            PerZA = ', ' + anket_dict.get('Перечислите перенесённые и хронические заболевания', '')
            PerZ += PerZA

        PerO = 'отрицает'
        PerOQ = anket_dict.get('У вас были операции раньше, в том числе пластические?', 'Нет')
        if PerOQ != 'Нет':
            PerO = anket_dict.get('Перечислите перенесённые операции', '')

        PerT = 'отрицает'
        PerTQ = anket_dict.get('У вас были травмы?', 'Нет')
        if PerTQ != 'Нет':
            PerT = anket_dict.get('Перечислите перенесённые ранее травмы', '')

        PerG = 'отрицает'
        PerGQ = anket_dict.get('Вы переносили гемотрансфузии?', 'Нет')
        if PerGQ != 'Нет':
            PerG = anket_dict.get('Перечислите перенесённые ранее гемотрансфузии', '')

        Allerg = 'аллергия отсутствует'
        AllergQ = anket_dict.get('Были ли у Вас аллергические реакции?', 'Нет')
        if AllergQ != 'Нет':
            Allerg = anket_dict.get('На что были аллергические реакции?', '')

        VICH = 'отрицает'
        VICHQ = anket_dict.get('Являетесь ли Вы носителем ВИЧ-инфекции?', 'Нет')
        if VICHQ != 'Нет':
            VICH = 'ВИЧ-носитель'

        Gepatit = 'отрицает'
        GepatitQ = anket_dict.get('Болели ли вы гепатитом?', 'Нет')
        if GepatitQ != 'Нет':
            Gepatit = 'гепатит типа ' + anket_dict.get('Гепатитом какого типа вы болели?', '')

        Tub = 'отрицает'
        TubQ = anket_dict.get('Болели ли вы туберкулёзом лёгких?', 'Нет')
        if TubQ != 'Нет':
            Tub = 'положительно'

        Diabet = 'отрицает'
        DiabetQ = anket_dict.get('У вас есть сахарный диабет?', 'Нет')
        if DiabetQ != 'Нет':
            Diabet = anket_dict.get('Сахарный диабет какого типа и когда был диагностирован?', '')

        Vener = 'отрицает'
        VenerQ = anket_dict.get('Болели ли Вы венерическими заболеваниями?', 'Нет')
        if VenerQ != 'Нет':
            Vener = anket_dict.get('Какие венерические заболевания Вы перенесли?', '')

        Alk = anket_dict.get('Отношение к алкоголю', 'отрицательно')
        Kur = anket_dict.get('Отношение к курению', 'отрицательно')
        Nark = anket_dict.get('Отношение к наркотикам', 'отрицательно')

        MedPrep = 'не принимаю'
        MedPrepQ = anket_dict.get('Вы принимаете какие-то лекарственные препараты на постоянной основе?', 'Нет')
        if MedPrepQ != 'Нет':
            MedPrep = anket_dict.get('Какие лекарственные препараты вы принимаете на постоянной основе?', '')

        MedIzd = 'отсутствуют'
        MedIzdQ = anket_dict.get('У вас имеются имплантированные медицинские изделия?', 'Нет')
        if MedIzdQ != 'Нет':
            MedIzd = anket_dict.get('Какие имплантированные медицинские изделия у вас имеются?', '')

        Gender = anket_dict.get('Пол', '')

        oGender = 'Мочеполовая система в норме'
        if Gender == 'женский':
            oGender = 'Менструации регулярные, беременность отрицает'

        Rost = anket_dict.get('Ваш рост (см)', '')
        Massa = anket_dict.get('Ваш вес (кг)', '')
        GK = anket_dict.get('Группа крови', '')
        RH = anket_dict.get('Резус-фактор', '')
        KELL = anket_dict.get('Келл-фактор', '')

        initial = {'FIO': fio,
                   'phone': phone,
                   'DateOfB': res_date,
                   'Address': Address,
                   'AddressRow': AddressRow,
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
                   'MedPrep': MedPrep,
                   'MedIzd': MedIzd,
                   'Rost': Rost,
                   'Massa': Massa,
                   'GK': GK,
                   'RH': RH,
                   'KELL': KELL,
                   'Gender': Gender,
                   'oGender': oGender,
                   'veSub': veSub,
                   'veRn': veRn,
                   'veGor': veGor,
                   'veNP': veNP,
                   'veUl': veUl,
                   'veDom': veDom,
                   'veStr': veStr,
                   'veKv': veKv,
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
               'state': anket_qs['state'],
               }
    template_name = 'crm/_quest.html'
    return render(request, template_name=template_name, context=context)


def recording_view(request, date=''):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    template_name = 'crm/_record.html'
    today = datetime.datetime.today().date()
    date = request.GET.get('date', None)
    if date:
        today = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    form = CandidateForm(initial={'date_oper': today})
    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            new_date = form.cleaned_data['date_oper']
            form.save()
            return redirect(reverse(timeline_view, args=(new_date,)))
    context = {'form': form,
               'title': 'Запись на операцию',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'today': today,
               }
    return render(request, template_name=template_name, context=context)


def updrecord_view(request, pk):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    template_name = 'crm/_record.html'
    current_candidate = Candidate.objects.get(pk=pk)
    form = CandidateForm(instance=current_candidate)
    if request.method == 'POST':
        form = CandidateForm(request.POST, instance=current_candidate)
        if form.is_valid():
            new_date = form.cleaned_data['date_oper']
            form.save()
            return redirect(reverse(timeline_view, args=(new_date,)))
    context = {'form': form,
               'title': 'Запись на операцию',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'current_candidate': current_candidate,
               }
    return render(request, template_name, context)


def delrecord_view(request, pk):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    if pk:
        current_candidate = get_object_or_404(Candidate, pk=pk)
        current_date = current_candidate.date_oper
        current_candidate.delete()
        return redirect(reverse(timeline_view, args=(current_date,)))


def timeline_view(request, set_date=''):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    template_name = 'crm/_timeline.html'
    today = datetime.datetime.today().date()
    if not set_date:
        set_date = today
    else:
        set_date = datetime.datetime.strptime(set_date, "%Y-%m-%d")
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    # выбираем все записи на операции, сортируя по возрастанию
    records = Candidate.objects.all().order_by('date_oper')
    first_rec = records[0].date_oper  # первая запись
    last_rec = records.reverse()[0].date_oper  # последняя запись
    start_of_records = datetime.datetime(first_rec.year, first_rec.month, 1)  #определяем начало месяца первой записи
    end_of_records = datetime.datetime(last_rec.year+2, 1, 31)  #определяем конец диапазона на основании последней записи
    current_date = start_of_records
    current_month = start_of_records.month

    rec_list = []
    rec_month = []
    # делаем последовательность дат записей для каждого месяца
    delta = datetime.timedelta(days=1)
    while current_date <= end_of_records:
        if current_month == current_date.month:
            date_rec = records.filter(date_oper=current_date)
            rec_month.append([current_date, date_rec if len(date_rec) > 0 else ''])
            current_date += delta
        else:
            rec_list.append(rec_month)
            rec_month = []
            current_month = current_date.month
    paginator = Paginator(rec_list, 1)
    current_page = request.GET.get('page', 0)
    # print(current_page)
    if current_page == 0:
        for page in paginator:
            first_day_on_page = page.object_list[0][0][0]
            if (first_day_on_page.year == set_date.year) and (first_day_on_page.month == set_date.month):
                current_page = page.number
    b_rec = paginator.get_page(current_page)
    enum_rec = paginator.get_elided_page_range(current_page, on_each_side=1, on_ends=1)


    if b_rec.has_previous():
        prev_page = b_rec.previous_page_number
        prev_page = prev_page()
    else:
        prev_page = 1
    if b_rec.has_next():
        next_page = b_rec.next_page_number
        next_page = next_page()
    else:
        next_page = paginator.num_pages

    num_week = 1
    # table = CandidateTable(Candidate.objects.all())

    context = {
               # 'table': table,
               'title': 'Расписание операций',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'today': today,
               'b_rec': b_rec,
               'enum_rec': enum_rec,
               'current_page': int(current_page),
               'prev_page_url': f'{reverse("timeline")}?page={prev_page}',
               'next_page_url': f'{reverse("timeline")}?page={next_page}',
               }
    return render(request, template_name=template_name, context=context)


def loadrec_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            data_file = os.path.join(settings.BASE_DIR, 'crm\\122023_load.csv')
            rec_list = []
            with open(data_file, encoding='utf-8') as file:
                csv_data = csv.reader(file, delimiter=';')
                for row in csv_data:
                    Candidate.objects.create(date_oper=datetime.datetime.strptime(row[0], "%d.%m.%Y"),
                                             phoneNumber=row[5], Sname=row[2], Name=row[3], Mname=row[4],
                                             Surgeon=row[7], notes=f'{row[1]} / {row[6]} ')

        return render(request, 'crm/import.html')
    else:
        form = UploadForm()
        return render(request, 'crm/import.html', {'form': form})