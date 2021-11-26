from lxml import html
from pprint import pprint
import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient('127.0.0.1', 27017)

db = client['news_mail']

up_news = db.up_news

up_news.create_index('link', unique=True)

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

url = 'https://news.mail.ru'

response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

mail_news = dom.xpath("//td[contains(@class, 'daynews')]/div[contains(@class, 'daynews__item')] | "
                      "//ul[contains(@class, 'js-module')]/li[@class='list__item']")

news_list = []

for news in mail_news:
    mail_news_info = {}
    link = news.xpath(".//a/@href")[0]

    response_news = requests.get(link, headers=header)
    dom_news = html.fromstring(response_news.text)

    name = dom_news.xpath("//h1/text()")
    date = dom_news.xpath("//span/@datetime")
    source = dom_news.xpath("//a[@class= 'link color_gray breadcrumbs__link']/span[@class='link__text']/text()")

    _id = link.split('/')[-2]

    mail_news_info['_id'] = _id
    mail_news_info['name'] = name[0]
    mail_news_info['link'] = link
    mail_news_info['date'] = date[0].split('T')[0]
    mail_news_info['source'] = source[0]

    news_list.append(mail_news_info)

    try:
        up_news.insert_one(mail_news_info)
    except DuplicateKeyError:
        print(f"The news with id {mail_news_info['_id']} already exists")

pprint(len(news_list))

for doc in up_news.find({}):
    pprint(doc)

print(up_news.count_documents({}))
