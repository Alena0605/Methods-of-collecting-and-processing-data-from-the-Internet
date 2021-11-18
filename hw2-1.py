# https://hh.ru/search/vacancy?clusters=true&ored_clusters=true&enable_snippets=true&salary=&text=Big+data
# https://hh.ru/search/vacancy?clusters=true&ored_clusters=true&enable_snippets=true&salary=&text=python

import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd

vacancy_hh = 'Big Data'

params = {
    'clusters': 'true',
    'ored_clusters': 'true',
    'enable_snippets': 'true',
    'salary': '',
    'text': vacancy_hh
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

url = 'https://hh.ru'

response = requests.get(url + '/search/vacancy', params=params, headers=headers)

dom = BeautifulSoup(response.text, 'html.parser')

page = 0
page_count = int(dom.find_all('span', {'class': 'pager-item-not-in-short-range'})[3].getText())

vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

vacancies_list = []

while page <= page_count:
    params['page'] = page
    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:
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
        vacancy_data['city'] = str(city[0])
        vacancy_data['metro'] = metro_station
        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['currency'] = currency
        vacancy_data['site'] = 'hh.ru'

        vacancies_list.append(vacancy_data)

    page += 1

pprint(vacancies_list)

width = 320
pd.set_option('display.width', width)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

df = pd.DataFrame(vacancies_list)

print(df.head(100))
