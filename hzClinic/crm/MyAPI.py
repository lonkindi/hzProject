import json
import requests
from hzClinic import settings_local


def get_ankets_myapi(state):
    req_data = settings_local.LoginAPI
    req_login = requests.post('https://hzapi.hotyanznaet.ru/login', data=req_data)
    token = json.loads(req_login.text)['Token']
    headers = {'Authorization': 'Token ' + token}
    if state == 0:
        req_ankets = requests.get('https://hzapi.hotyanznaet.ru/ankets?state=0', headers=headers)
    elif state == 1:
        req_ankets = requests.get('https://hzapi.hotyanznaet.ru/ankets?state=1', headers=headers)
    else:
        req_ankets = requests.get('https://hzapi.hotyanznaet.ru/ankets', headers=headers)
    str_dict = req_ankets.text[1:-2]
    lst_req = str_dict.split(sep='},')
    return lst_req


def get_anket_myapi(ext_id):
    req_data = settings_local.LoginAPI
    req_login = requests.post('https://hzapi.hotyanznaet.ru/login', data=req_data)
    token = json.loads(req_login.text)['Token']
    headers = {'Authorization': 'Token ' + token}
    req_anket = requests.get(f'https://hzapi.hotyanznaet.ru/anket?ext_id={ext_id}', headers=headers)
    str_dict = req_anket.text[1:-2]
    lst_req = str_dict.split(sep='},')
    return lst_req


def update_anket_myapi(ext_id, state):
    req_data = settings_local.LoginAPI
    req_login = requests.post('https://hzapi.hotyanznaet.ru/login', data=req_data)
    token = json.loads(req_login.text)['Token']
    headers = {'Authorization': 'Token ' + token}
    req_anket = requests.put(f'https://hzapi.hotyanznaet.ru/putanket?id={ext_id}&state={state}', headers=headers)
    str_dict = req_anket.text[1:-2]
    lst_req = str_dict.split(sep='},')
    return lst_req


def get_analyzes_myapi(PHONE):
    req_data = settings_local.LoginAPI
    req_login = requests.post('https://hzapi.hotyanznaet.ru/login', data=req_data)
    token = json.loads(req_login.text)['Token']
    headers = {'Authorization': 'Token ' + token, 'PHONE': PHONE}
    req_ankets = requests.post('https://hzapi.hotyanznaet.ru/getanalyzes', headers=headers)
    str_dict = req_ankets.text[1:-2]
    lst_req = str_dict.split(sep='},')
    return lst_req