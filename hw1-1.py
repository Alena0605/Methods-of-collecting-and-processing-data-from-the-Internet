"""
1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json.
"""

import requests
import json

url = 'https://api.github.com'
username = 'Alena0605'

response = requests.get(f'{url}/users/{username}/repos')
response_json = response.json()

with open('hw1-1.json', 'w') as f:
    json.dump(response_json, f)

with open('hw1-1.json', 'r') as f:
    j_file = json.load(f)
    print(f'Список репозиториев пользователя {username}: ')
    for i in j_file:
        print(i['name'])
