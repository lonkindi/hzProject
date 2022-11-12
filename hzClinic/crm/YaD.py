import os
import requests
from datetime import datetime
from hzClinic import settings_local

URL = 'https://cloud-api.yandex.net/v1/disk/resources'
TOKEN = settings_local.YaTOKEN
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}

def create_folder(path):
    """Создание папки.
    path: Путь к создаваемой папке."""
    requests.put(f'{URL}?path={path}', headers=headers)

def upload_file(loadfile, savefile, replace=False):
    """Загрузка файла.
    savefile: Путь к файлу на Диске
    loadfile: Путь к загружаемому файлу
    replace: true or false Замена файла на Диске"""
    res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
    with open(loadfile, 'rb') as f:
        try:
            requests.put(res['href'], files={'file':f})
        except KeyError:
            print(res)
if __name__ == '__main__':
    pass
