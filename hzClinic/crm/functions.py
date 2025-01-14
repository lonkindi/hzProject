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

from crm.models import TypeOperations, Doctor
from crm import YaD, MyAPI

from hzClinic import settings, settings_local


def fill_tmpl(oper_list, context_dict):
    sFIO = translit(context_dict['sFIO'], 'ru', reversed=True)
    sOpers = translit(context_dict['sOpers'], 'ru', reversed=True)
    doc_folder = sFIO + '_' + sOpers + '_' + context_dict['sDate0']
    base_dir = settings.BASE_DIR
    file_path = os.path.join(base_dir, 'crm/tmpls/')
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
    if context_dict['schema'] == 'голова':
        items.append('schemeG')
    elif context_dict['schema'] == 'тело':
        items.append('schemeT')
    elif context_dict['schema'] == 'голова + тело':
        items.append('schemeG')
        items.append('schemeT')
    for item in items:
        doc = DocxTemplate(file_path + item + '.docx')
        doc.render(context_dict)
        doc.save(docs_path + doc_folder + '/' + item + '_' + sFIO + '.docx')

    id_ext = int(context_dict.get('anket_id', 0))


    if id_ext:
        MyAPI.update_anket_myapi(ext_id=id_ext, state=0) # исправить статус!!!

    YaD.create_folder(f'MedicalCase/{doc_folder}')
    for file in os.listdir(target_path):
        upload_file = target_path + '/' + file
        YaD.upload_file(upload_file, f'MedicalCase/{doc_folder}/{file}')
    # print('YaD.get_folder = ', YaD.get_folder(f'MedicalCase/{doc_folder}'))
    # print('YaD.delete_folder =', YaD.delete_folder(f'MedicalCase/{doc_folder}'))
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
    oper_date_str = query_dict.get('date_oper', False)
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

    docs_context['anest'] = query_dict.get('anest', False)
    docs_context['schema'] = query_dict.get('schema', False)

    docs_context['id_ext'] = query_dict.get('id_ext', False)
    docs_context['anket_id'] = query_dict.get('anket_id', False)
    docs_context['PerZ'] = query_dict.get('PerZ', False)
    docs_context['PerO'] = query_dict.get('PerO', False)
    docs_context['PerT'] = query_dict.get('PerT', False)
    docs_context['PerG'] = query_dict.get('PerG', False)
    docs_context['Allerg'] = query_dict.get('Allerg', False)
    docs_context['Kur'] = query_dict.get('Kur', False)
    docs_context['Alk'] = query_dict.get('Alk', False)
    docs_context['Nark'] = query_dict.get('Nark', False)
    docs_context['Gepatit'] = query_dict.get('Gepatit', False)
    docs_context['Risk'] = query_dict.get('Risk', False)
    docs_context['VICH'] = query_dict.get('VICH', False)
    docs_context['Tub'] = query_dict.get('Tub', False)
    docs_context['Diabet'] = query_dict.get('Diabet', False)
    docs_context['Vener'] = query_dict.get('Vener', False)

    docs_context['sDate0'] = re.sub('\D', '', docs_context['Date0'])
    docs_context['FIO'] = query_dict.get('s_name', False) + ' ' +query_dict.get('name', False) + ' ' +query_dict.get('m_name', False)
    docs_context['sFIO'] = re.sub(r'\b(\w+)\b\s+\b(\w)\w*\b\s+\b(\w)\w*\b', r'\1\2\3', docs_context['FIO'])
    docs_context['IO'] = re.sub(r'\b(\w+)\b\s+\b(\w*)\w*\b\s+\b(\w*)\w*\b', r'\2 \3', docs_context['FIO'])

    typeOpers = query_dict.getlist('typeOpers', False)
    sum_opers = '-'
    for oper in TypeOperations.objects.all():
        if str(oper.code) in typeOpers:
            selected_operations.append(oper)
            sum_opers += (oper.s_name + '-')

    docs_context['sOpers'] = sum_opers[1:-1]
    docs_context['DR'] = datetime.datetime.strptime(query_dict.get('DateOfB', False), "%Y-%m-%d").strftime('%d.%m.%Y')
    docs_context['DG'] = docs_context['DR'][6:]
    docs_context['Adr'] = query_dict.get('Address', False)
    docs_context['Gender'] = query_dict.get('Gender', False)
    docs_context['oGender'] = query_dict.get('oGender', False)
    docs_context['MedPrep'] = query_dict.get('MedPrep', False)
    docs_context['MedIzd'] = query_dict.get('MedIzd', False)
    docs_context['veSub'] = query_dict.get('veSub', False)
    docs_context['veRn'] = query_dict.get('veRn', False)
    docs_context['veGor'] = query_dict.get('veGor', False)
    docs_context['veNP'] = query_dict.get('veNP', False)
    docs_context['veUl'] = query_dict.get('veUl', False)
    docs_context['veDom'] = query_dict.get('veDom', False)
    docs_context['veStr'] = query_dict.get('veStr', False)
    docs_context['veKv'] = query_dict.get('veKv', False)
    docs_context['Rost'] = query_dict.get('Rost', False)
    docs_context['Massa'] = query_dict.get('Massa', False)
    docs_context['GK'] = query_dict.get('GK', False)
    docs_context['RH'] = query_dict.get('RH', False)
    docs_context['KELL'] = query_dict.get('KELL', False)
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
    med_vmesh = ''
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
        # print(f'primen_lec=>{primen_lec}<')
        primen_lec += selector + curr_operation.primen_lec

        # print(f'med_vmesh=>{med_vmesh}<***oper=>{operation}<')
        if med_vmesh == '':
            selector = ''
        else:
            selector = ';'
        med_vmesh += selector + (curr_operation.med_vmesh if curr_operation.med_vmesh is not None else '')

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
    # print(f'med_vmesh 1={med_vmesh}')
    med_vmesh = del_duplicates(med_vmesh, ';')
    # print(f'med_vmesh 2={med_vmesh}')
    for item in day_list:
        primen_lec_str = primen_lec.replace(f'{"{Date"+str(item)+"}"}', docs_context['Date' + str(item)])
        med_vmesh_str = med_vmesh.replace(f'{"{Date"+str(item)+"}"}', docs_context['Date' + str(item)])
        primen_lec = primen_lec_str
        med_vmesh = med_vmesh_str
    # print(f'med_vmesh 3={med_vmesh}')
    docs_context['primen_lec'] = primen_lec
    docs_context['med_vmesh'] = med_vmesh

    for i in range(1, 8):
        docs_context['ln_lp' + str(i)] = '\r\n\r\n'
        docs_context['ln_mv' + str(i)] = '\r\n\r\n'

    for index, value in enumerate(primen_lec.split(';')):
        ln_lp = re.search(r'(.*?) с ', value)
        ln_Date_n = re.search(r'с (\d\d.\d\d.*?) г.', value)
        ln_Date_o = re.search(r'по (\d\d.\d\d.*?) г.', value)
        docs_context['ln_lp' + str(index+1)] = ln_lp.group(1) if ln_lp else '\r\n\r\n'
        docs_context['ln_Date' + str(index+1) + '_n'] = ln_Date_n.group(1)+' г.\r\n__________' if ln_Date_n else ''
        docs_context['ln_Date' + str(index+1) + '_o'] = ln_Date_o.group(1)+' г.\r\n__________' if ln_Date_o else ''

    for index, value in enumerate(med_vmesh.split(';')):
        ln_mv = re.search(r'(.*?) на ', value)
        ln_Date_mv = re.search(r'на (\d\d.\d\d.*?) г.', value)

        docs_context['ln_mv' + str(index+1)] = ln_mv.group(1) if ln_mv else '\r\n\r\n'
        docs_context['ln_Date' + str(index+1) + '_mv'] = ln_Date_mv.group(1)+' г.\r\n__________' if ln_Date_mv else ''

    docs_context['rezult'] = del_duplicates(rezult)
    propis = {1: 'одни', 2: 'двое', 3: 'трое', 4: 'четверо', 5: 'пятеро', 6: 'шестеро', 7: 'семеро', 8: 'восемь', }
    if srok_gosp == 1:
        sutok = ' сутки'
    else:
        sutok = ' суток'
    docs_context['srok_gosp'] = str(srok_gosp) + f' ({propis.get(srok_gosp, False)}) ' + sutok
    docs_context['PZK'] = query_dict.get('PZK', False)
    doctor = Doctor.objects.filter(pk=int(query_dict.get('surgeon', False)))[0]
    # docs_context['surgeon'] = doctor
    docs_context['doc_F'] = doctor.F_name
    docs_context['doc_I'] = doctor.L_name
    docs_context['doc_O'] = doctor.S_name
    docs_context['doc_pos'] = doctor.position
    docs_context['doc_spec'] = doctor.specialty
    docs_context['doc_inic'] = doctor.L_name[:1] + '.' + doctor.S_name[:1]+'.'
    doc_F_list = list(doctor.F_name_padezhi.split(','))
    doc_L_list = list(doctor.L_name_padezhi.split(','))
    doc_S_list = list(doctor.S_name_padezhi.split(','))
    docs_context['doc_F_R'] = doc_F_list[0]
    docs_context['doc_I_R'] = doc_L_list[0]
    docs_context['doc_O_R'] = doc_S_list[0]
    docs_context['doc_F_D'] = doc_F_list[1]
    docs_context['doc_I_D'] = doc_L_list[1]
    docs_context['doc_O_D'] = doc_S_list[1]
    docs_context['doc_F_T'] = doc_F_list[2]
    docs_context['doc_I_T'] = doc_L_list[2]
    docs_context['doc_O_T'] = doc_S_list[2]
    docs_context['doc_F_P'] = doc_F_list[3]
    docs_context['doc_I_P'] = doc_L_list[3]
    docs_context['doc_O_P'] = doc_S_list[3]
    # print(f'docs_context = {docs_context}')
    ya_folder = fill_tmpl(selected_operations, docs_context)
    return ya_folder
    # send_telegram('Hello BOT!')


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
