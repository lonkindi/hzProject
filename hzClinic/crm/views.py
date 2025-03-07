import ast
import datetime
import os
import re
import csv

from dadata import Dadata
from dateutil.relativedelta import relativedelta
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator

from crm.forms import LoginForm, QuestForm, CandidateForm, UploadForm, MedCardForm
from crm.models import hzUserInfo, TypeOperations, Candidate, MedCard
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from crm import YaD, MyAPI, functions

from hzClinic import settings, settings_local


def page_not_found_view(request, exception):
    return render(request, 'crm/404.html', status=404)


def main_view(request):
    return redirect(reverse(timeline_view)) #временная заглушка dashboard

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
    paginator = Paginator(analizes_list, 10)
    current_page = request.GET.get('page', 1)
    b_analyzes = paginator.get_page(current_page)
    e_analyzes = paginator.get_elided_page_range(current_page, on_each_side=1, on_ends=1)
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
    context = {'title': 'Результаты анализов',
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
    else:
        ankets = MyAPI.get_ankets_myapi(-1)
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


def quest_hide(request, ext_id):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    MyAPI.update_anket_myapi(ext_id=ext_id, state=1)
    return redirect(reverse('quests', args=[0]))


def quest_view(request, ext_id):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    if request.method == 'POST':
        form = MedCardForm(request.POST)
        if form.is_valid():
            new_medcard = form.save()
            current_folder = functions.do_docs(request.POST)
            ya_folder = f'https://disk.yandex.ru/client/disk/MedicalCase/{current_folder}'
            new_medcard.ya_folder = ya_folder
            new_medcard.save()
        else:
            pass
        return redirect(reverse('quests', args=[0]))

    else:
        anket = MyAPI.get_anket_myapi(ext_id) # list
        anket_str = anket[0].replace("'", '`')
        anket_qs = ast.literal_eval(anket_str.replace('"', "'") + '}')
        anket_dict = anket_qs['content']  # anket[0].content
        anket_id = ext_id
        content = anket_dict
        date_filling = anket_qs['date_filling']
        f = str(anket_dict.get('Фамилия', '!НЕТ!')).capitalize().strip()
        i = str(anket_dict.get('Имя', '!НЕТ!')).capitalize().strip()
        o = str(anket_dict.get('Отчество', '')).capitalize().strip()
        fio = f + ' ' + i + ' ' + o
        raw_phone = anket_dict.get('Ваш контактный телефон', '')
        phone = re.sub('[\D]+','', raw_phone)
        today = datetime.date.today()
        anest = ''
        schema = ''
        typeOpers = ''
        date_oper = ''
        surgeon = ''
        find_candidate = Candidate.objects.filter(phoneNumber=phone, date_oper__gte=today).order_by('date_oper')
        if find_candidate:
            find_candidate = find_candidate[0]
            date_oper = find_candidate.date_oper
            typeOpers = find_candidate.typeOpers.all()
            surgeon = find_candidate.Doctor

        AddressRow = anket_dict['Адрес места жительства (регистрации)']
        token = settings_local.DaDaAPI
        secret = settings_local.DaDaSecret
        dadata = Dadata(token, secret)
        result = dadata.clean("address", AddressRow)
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

        res_date = datetime.datetime.strptime(anket_dict['Дата рождения'], "%Y-%m-%d").date()
        fill_date = datetime.datetime.strptime(date_filling, "%Y-%m-%d").date()
        PerZ = 'ОРВИ'
        PerZQ = anket_dict.get('Перенесённые и хронические заболевания?', 'Нет')
        if PerZQ != 'Нет':
            PerZA = ', ' + anket_dict.get('Перечислите перенесённые и хронические заболевания', '').lower()
            PerZ += PerZA

        PerO = 'отрицает'
        PerOQ = anket_dict.get('У вас были операции раньше, в том числе пластические?', 'Нет')
        if PerOQ != 'Нет':
            PerO = anket_dict.get('Перечислите перенесённые операции', '').lower()

        PerT = 'отрицает'
        PerTQ = anket_dict.get('У вас были травмы?', 'Нет')
        if PerTQ != 'Нет':
            PerT = anket_dict.get('Перечислите перенесённые ранее травмы', '').lower()

        PerG = 'отрицает'
        PerGQ = anket_dict.get('Вы переносили гемотрансфузии?', 'Нет')
        if PerGQ != 'Нет':
            PerG = anket_dict.get('Перечислите перенесённые ранее гемотрансфузии', '').lower()

        Allerg = 'аллергия отсутствует'
        AllergQ = anket_dict.get('Были ли у Вас аллергические реакции?', 'Нет')
        if AllergQ != 'Нет':
            Allerg = anket_dict.get('На что были аллергические реакции?', '').lower()

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
            Vener = anket_dict.get('Какие венерические заболевания Вы перенесли?', '').lower()

        Alk = anket_dict.get('Отношение к алкоголю', 'отрицательно')
        Kur = anket_dict.get('Отношение к курению', 'отрицательно')
        Nark = anket_dict.get('Отношение к наркотикам', 'отрицательно')

        MedPrep = 'не принимаю'
        MedPrepQ = anket_dict.get('Вы принимаете какие-то лекарственные препараты на постоянной основе?', 'Нет')
        if MedPrepQ != 'Нет':
            MedPrep = anket_dict.get('Какие лекарственные препараты вы принимаете на постоянной основе?', '').lower()

        MedIzd = 'отсутствуют'
        MedIzdQ = anket_dict.get('У вас имеются имплантированные медицинские изделия?', 'Нет')
        if MedIzdQ != 'Нет':
            MedIzd = anket_dict.get('Какие имплантированные медицинские изделия у вас имеются?', '').lower()

        Gender = anket_dict.get('Пол', '')

        oGender = 'Мочеполовая система в норме'
        if Gender == 'женский':
            oGender = 'Менструации регулярные, беременность отрицает'

        Rost = anket_dict.get('Ваш рост (см)', '')
        Massa = anket_dict.get('Ваш вес (кг)', '')
        GK = anket_dict.get('Группа крови', '')
        RH = anket_dict.get('Резус-фактор', '')
        KELL = anket_dict.get('Келл-фактор', '')

        initial = {'anket_id': anket_id,
                   'content': content,
                   'date_filling': fill_date,
                   's_name': f,
                   'name': i,
                   'm_name': o,
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
                   'date_oper': date_oper,
                   'anest': anest,
                   'schema': schema,
                   'typeOpers': typeOpers,
                   'surgeon': surgeon,
                   'candidate': find_candidate,
                   }
        form = list(MedCardForm(initial=initial))
    oper_types = TypeOperations.objects.all()
    today = datetime.datetime.today().date().strftime("%Y-%m-%d")
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    context = {'title': 'Анкета',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'today': today,
               'date_filling': fill_date,
               'oper_types': oper_types,
               'form': form,
               'ext_id': ext_id,
               'FIO': fio,
               'state': anket_qs['state'],
               'find_candidate': find_candidate,
               }
    template_name = 'crm/_quest.html'
    return render(request, template_name=template_name, context=context)


def medcard_view(request, pk):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    template_name = 'crm/_medcard.html'
    current_medcard = get_object_or_404(MedCard, anket_id=pk)
    form = list(MedCardForm(instance=current_medcard))
    new_date = datetime.datetime.today().date()
    if request.method == 'POST':
        form = MedCardForm(request.POST, instance=current_medcard)
        if form.is_valid():
            curr_medcard = form.save()
            current_folder = functions.do_docs(request.POST)
            ya_folder = f'https://disk.yandex.ru/client/disk/MedicalCase/{current_folder}'
            curr_medcard.ya_folder = ya_folder
            curr_medcard.save()
            new_date = form.cleaned_data['date_oper']
        else:
            pass
        return redirect(reverse(timeline_view, args=(new_date,)))
    context = {'form': form,
               'title': 'Медицинская карта',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'current_medcard': current_medcard,
               }
    return render(request, template_name, context)


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

    #добаляем в порцию пагинатора суммарную длительность за день
    for rec in b_rec[0]:
        if rec[1] is None:
            rec.append(0)
        else:
            day_duration = 0
            for candidat in rec[1]:
                day_duration += candidat.total_duration
            rec.append(day_duration)

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
    context = {
               # 'total_duration': total_duration,
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


def export_tl_view(request, encrypt_dates=None):
    s_date = ''
    e_date = ''
    public_link = ''
    template = 'crm/_content_export_tl.html'
    # if not request.user.is_authenticated:
    #     return redirect(reverse(login_view))
    if request.method == 'POST':
        str_s_date = request.POST['start_date']
        str_e_date = request.POST['end_date']
        s_date = datetime.datetime.strptime(str_s_date, "%Y-%m-%d").date()
        e_date = datetime.datetime.strptime(str_e_date, "%Y-%m-%d").date()
        str_date = f'{str_s_date}/{str_e_date}'
        public_link = f'{functions.encrypt(str_date)}'
    else:
        if encrypt_dates:
            str_dates = functions.decrypt(encrypt_dates)
            # if not str_dates:
            #     return HttpResponseNotFound('<h1>Страница не найдена</h1>')
            try:
                s_date = datetime.datetime.strptime(str_dates[:10], "%Y-%m-%d").date()
                e_date = datetime.datetime.strptime(str_dates[11:], "%Y-%m-%d").date()
                public_link = f'{encrypt_dates}'
            except Exception as e:
                return HttpResponseNotFound(f'<h1>Страница не найдена</h1>')
    try:
        data = Candidate.objects.filter(date_oper__gte=s_date) & Candidate.objects.filter(date_oper__lte=e_date)
    except Exception as e:
        return HttpResponseNotFound(f'<h1>Некорректная ссылка</h1>')
    context = {
        'start_date': s_date,
        'end_date': e_date,
        'data': data,
        'public_link': public_link,
    }
    return render(request, template, context)


def control_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse(login_view))
    hzuser = request.user
    hzuser_info = hzUserInfo.objects.filter(hz_user=hzuser)
    template_name = 'crm/_control.html'
    today = datetime.date.today()
    date_ctrl_3 = [today + relativedelta(months=-3, days=-3), today + relativedelta(months=-3)]
    date_ctrl_6 = [today + relativedelta(months=-6, days=-3), today + relativedelta(months=-6)]
    date_ctrl_12 = [today + relativedelta(months=-12, days=-3), today + relativedelta(months=-12)]
    data_3 = Candidate.objects.filter(date_oper__gte=date_ctrl_3[0]) & Candidate.objects.filter(
        date_oper__lte=date_ctrl_3[1])
    data_6 = Candidate.objects.filter(date_oper__gte=date_ctrl_6[0]) & Candidate.objects.filter(
        date_oper__lte=date_ctrl_6[1])
    data_12 = Candidate.objects.filter(date_oper__gte=date_ctrl_12[0]) & Candidate.objects.filter(
        date_oper__lte=date_ctrl_12[1])

    # if request.method == 'POST':
    #     # form = CandidateForm(request.POST, instance=current_candidate)
    #     if form.is_valid():
    #         new_date = form.cleaned_data['date_oper']
    #         form.save()
    #         return redirect(reverse(timeline_view, args=(new_date,)))
    context = {'title': 'Контроль прооперированных пациентов',
               'user': hzuser,
               'user_info': hzuser_info[0],
               'data_3': data_3,
               'data_6': data_6,
               'data_12': data_12,
               }
    return render(request, template_name, context)

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
