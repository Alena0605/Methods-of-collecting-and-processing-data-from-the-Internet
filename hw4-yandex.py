from lxml import html
from pprint import pprint
import requests
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient('127.0.0.1', 27017)

db = client['yandex']

main_news = db.main_news

main_news.create_index('link', unique=True)

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

url = 'https://yandex.ru/news'

response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

yandex_news = dom.xpath("//div[contains(@class, 'news-top-flexible-stories')]/div[contains(@class, 'mg-grid__col')]")

news_list = []

now = datetime.now()
now_date = now.strftime("%Y-%m-%d %H:%M").split(' ')[0]

for news in yandex_news:
    yandex_news_info = {}
    name = news.xpath(".//h2/text()")
    link = news.xpath(".//h2/../@href")
    date = now_date
    source = news.xpath(".//span[@class='mg-card-source__source']//a/text()")

    yandex_news_info['name'] = name[0].replace('\xa0', ' ')
    yandex_news_info['link'] = link[0]
    yandex_news_info['date'] = date
    yandex_news_info['source'] = source[0]

    news_list.append(yandex_news_info)

    try:
        main_news.insert_one(yandex_news_info)
    except DuplicateKeyError:
        print(f"The news with id {yandex_news_info['_id']} already exists")

pprint(len(news_list))

for doc in main_news.find({}):
    pprint(doc)

print(main_news.count_documents({}))
