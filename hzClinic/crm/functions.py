import base64
import os
import datetime
from io import BytesIO

import requests
import random
import re

from cryptography.fernet import Fernet
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from transliterate import translit
from docxtpl import DocxTemplate

from crm.models import TypeOperations

from hzClinic import settings, settings_local


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


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise RuntimeError(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def encrypt(txt):
    try:
        # convert integer etc to string first
        txt = str(txt)
        # get the key from settings
        cipher_suite = Fernet(settings_local.ENCRYPT_KEY)  # key should be byte
        # #input should be byte, so convert the text to byte
        encrypted_text = cipher_suite.encrypt(txt.encode('ascii'))
        # encode to urlsafe base64 format
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
        return encrypted_text
    except Exception as e:
        # log the error if any
        # logging.getLogger("error_logger").error(traceback.format_exc())
        return None


def decrypt(txt):
    try:
        # base64 decode
        txt = base64.urlsafe_b64decode(txt)
        cipher_suite = Fernet(settings_local.ENCRYPT_KEY)
        decoded_text = cipher_suite.decrypt(txt).decode("ascii")
        return decoded_text
    except Exception as e:
        # log the error
        # logging.getLogger("error_logger").error(traceback.format_exc())
        return None
