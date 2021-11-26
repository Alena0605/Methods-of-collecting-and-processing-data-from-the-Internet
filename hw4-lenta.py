from lxml import html
from pprint import pprint
import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient('127.0.0.1', 27017)

db = client['lenta']

front_news = db.front_news

front_news.create_index('link', unique=True)

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

url = 'https://lenta.ru'

response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

lenta_news = dom.xpath("//section[@class='row b-top7-for-main js-top-seven']//div[contains(@class, 'item')]")

news_list = []

for news in lenta_news:
    lenta_news_info = {}
    name = news.xpath(".//a/text()")
    link = news.xpath(".//a/@href")
    full_link = url + link[0]
    date = news.xpath(".//time[@class='g-time']/@datetime")
    source = 'https://lenta.ru'

    lenta_news_info['name'] = name[0].replace('\xa0', ' ')
    lenta_news_info['link'] = full_link
    lenta_news_info['date'] = date[0].split(',')[1]
    lenta_news_info['source'] = source

    news_list.append(lenta_news_info)

    try:
        front_news.insert_one(lenta_news_info)
    except DuplicateKeyError:
        print(f"The news with id {lenta_news_info['_id']} already exists")

pprint(len(news_list))

for doc in front_news.find({}):
    pprint(doc)

print(front_news.count_documents({}))
