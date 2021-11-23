"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
которая будет добавлять только новые вакансии/продукты в вашу базу.
"""

# https://hh.ru/search/vacancy?clusters=true&ored_clusters=true&enable_snippets=true&salary=&text=Big+data
# https://hh.ru/search/vacancy?clusters=true&ored_clusters=true&enable_snippets=true&salary=&text=python

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pprint import pprint
# import pandas as pd

client = MongoClient('127.0.0.1', 27017)

db = client['HeadHunter']

vacancies = db.vacancies

vacancies.create_index('link', unique=True)

vacancy_hh = input('Enter searching vacancy: ')  # 'Big Data'

params = {
    'clusters': 'true',
    'ored_clusters': 'true',
    'enable_snippets': 'true',
    'salary': '',
    'text': vacancy_hh,
    'items_on_page': 20
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

url = 'https://hh.ru'

response = requests.get(url + '/search/vacancy', params=params, headers=headers)

dom = BeautifulSoup(response.text, 'html.parser')

hh_vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

page = 0
# page_count = int(dom.find_all('span', {'class': 'pager-item-not-in-short-range'})[3].getText())

vacancies_list = []

while hh_vacancies:
    params['page'] = page
    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    hh_vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in hh_vacancies:
        vacancy_data = {}
        name_info = vacancy.find('a', {'class': 'bloko-link'})
        name = name_info.getText()
        link = name_info['href']
        employer = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).getText().replace('\xa0', ' ')
        city = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).getText().split(',')

        metro = vacancy.find('span', {'class': 'metro-station'})
        if not metro:
            metro_station = None
        else:
            metro_station = metro.getText()

        try:
            salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText().replace('\u202f', '')
            salary_split = salary.split()
            if salary.startswith('до'):
                salary_min = None
                salary_max = int(salary_split[1])
                currency = salary_split[2]
            elif salary.startswith('от'):
                salary_min = int(salary_split[1])
                salary_max = None
                currency = salary_split[2]
            else:
                salary_min = int(salary_split[0])
                salary_max = int(salary_split[2])
                currency = salary_split[3]
        except:
            salary_min = None
            salary_max = None
            currency = None

        vacancy_data['name'] = name
        vacancy_data['link'] = link
        vacancy_data['employer'] = employer
        vacancy_data['city'] = city[0]
        vacancy_data['metro'] = metro_station
        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['currency'] = currency
        vacancy_data['site'] = 'hh.ru'

        vacancies_list.append(vacancy_data)

        try:
            vacancies.insert_one(vacancy_data)
        except DuplicateKeyError:
            print(f"The vacancy with id {vacancy_data['_id']} already exists")

    page += 1

# pprint(vacancies_list)
print(len(vacancies_list))

for doc in vacancies.find({}):
    pprint(doc)

print(vacancies.count_documents({}))

# width = 320
# pd.set_option('display.width', width)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_colwidth', None)
#
# df = pd.DataFrame(vacancies_list)
#
# print(df.tail(100))

"""
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы 
(необходимо анализировать оба поля зарплаты). 
Для тех, кто выполнил задание с Росконтролем - напишите запрос для поиска продуктов с рейтингом не ниже введенного 
или качеством не ниже введенного (то есть цифра вводится одна, а запрос проверяет оба поля)
"""

searching_salary = int(input('Enter searching salary: '))

count = 0
for i in vacancies.find({'$or': [
                              {'salary_min': {'$gte': searching_salary}},
                              {'salary_max': {'$gte': searching_salary}}
                              ]}):
    pprint(i)
    count += 1

print(f"At your request it was found {count} vacancies.")
