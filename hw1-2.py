"""
2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию.
Ответ сервера записать в файл.

Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide).
Сделайте запрос, чтобы получить список всех сообществ на которые вы подписаны.
"""

import requests
import json

url = 'https://api.vk.com/method/groups.get?'
user_id = 337377270
access_token = input('Enter your access token:\n')
v = '5.124'

response = requests.get(f'{url}user_id={user_id}&extended=1&access_token={access_token}&v={v}')
response_json = response.json()

with open('hw1-2.json', 'w') as f:
    json.dump(response_json, f)

with open('hw1-2.json', 'r') as f:
    j_file = json.load(f)
    print(f'\nВы подписаны на {j_file["response"]["count"]} сообществ:')
    for group in j_file['response']['items']:
        print(f"{group['name']}")
