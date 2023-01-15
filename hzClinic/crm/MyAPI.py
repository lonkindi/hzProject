import json
import requests
from hzClinic import settings_local


def get_ankets_myapi(state):
    req_data = settings_local.LoginAPI
    req_login = requests.post('http://cr74664-django-l4m8f.tw1.ru/login', data=req_data)
    token = json.loads(req_login.text)['Token']
    headers = {'Authorization': 'Token ' + token}
    if state == 0:
        req_ankets = requests.get('http://cr74664-django-l4m8f.tw1.ru/ankets?state=0', headers=headers)
    elif state == 1:
        req_ankets = requests.get('http://cr74664-django-l4m8f.tw1.ru/ankets?state=1', headers=headers)
    else:
        req_ankets = requests.get('http://cr74664-django-l4m8f.tw1.ru/ankets', headers=headers)
    str_dict = req_ankets.text[1:-2]
    lst_req = str_dict.split(sep='},')
    return lst_req


def get_anket_myapi(ext_id):
    req_data = settings_local.LoginAPI
    req_login = requests.post('http://cr74664-django-l4m8f.tw1.ru/login', data=req_data)
    token = json.loads(req_login.text)['Token']
    headers = {'Authorization': 'Token ' + token}
    req_anket = requests.get(f'http://cr74664-django-l4m8f.tw1.ru/anket?ext_id={ext_id}', headers=headers)
    str_dict = req_anket.text[1:-2]
    lst_req = str_dict.split(sep='},')
    return lst_req

def update_anket_myapi(ext_id, state):
    req_data = settings_local.LoginAPI
    req_login = requests.post('http://cr74664-django-l4m8f.tw1.ru/login', data=req_data)
    token = json.loads(req_login.text)['Token']
    headers = {'Authorization': 'Token ' + token}
    req_anket = requests.put(f'http://cr74664-django-l4m8f.tw1.ru/putanket?id={ext_id}&state={state}', headers=headers)
    str_dict = req_anket.text[1:-2]
    lst_req = str_dict.split(sep='},')
    return lst_req
