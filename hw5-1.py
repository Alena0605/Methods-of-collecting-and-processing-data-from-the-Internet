"""
Вариант I
Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и
сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный).
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172#
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.common.exceptions import StaleElementReferenceException as sere
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta

driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(5)

driver.get('https://account.mail.ru/login')

elem = driver.find_element(By.NAME, 'username')
elem.send_keys('study.ai_172')
elem.send_keys(Keys.ENTER)

elem = driver.find_element(By.NAME, 'password')
elem.send_keys('NextPassword172#')
elem.send_keys(Keys.ENTER)

count_of_letters = driver.find_element(By.XPATH, "//div[@class='nav-folders']//a[1]").get_attribute('title').split(', ')[1].split(' ')[0]
print(count_of_letters)

messages_link = {}

try:
    while len(messages_link) != count_of_letters:
        messages = driver.find_elements(By.XPATH, "//div[@class='dataset__items']/a")

        for message in messages:
            link = message.get_attribute('href')
            _id = message.get_attribute('data-id')

            if _id is not None:
                messages_link[_id] = link

        actions = ActionChains(driver)
        actions.move_to_element(messages[-1])
        actions.perform()
        time.sleep(2)
except sere:
    pass

pprint(messages_link)
print(len(messages_link))

client = MongoClient('127.0.0.1', 27017)

db = client['mail_ru']

incoming_emails = db.incoming_emails

now = datetime.now()
now_date = now.strftime("%Y-%m-%d %H:%M").split(' ')[0]
yesterday = now - timedelta(1)
yesterday_date = yesterday.strftime("%Y-%m-%d %H:%M").split(' ')[0]

messages_list = []

for message in messages_link.items():
    messages_add_info = {}
    driver.get(message[1])

    from_whom = driver.find_element(By.XPATH, "//span[@class='letter-contact']").text
    date = driver.find_element(By.XPATH, "//div[@class='letter__date']").text.split(',')

    if date[0] == 'Сегодня':
        date[0] = now_date
    elif date[0] == 'Вчера':
        date[0] = yesterday_date

    subject = driver.find_element(By.XPATH, "//h2[@class='thread__subject']").text
    content = driver.find_element(By.XPATH, "//div[@class='letter__body']").text

    messages_add_info['_id'] = message[0]
    messages_add_info['from_whom'] = from_whom
    messages_add_info['date'] = ','.join(date)
    messages_add_info['subject'] = subject
    messages_add_info['content'] = content

    messages_list.append(messages_add_info)

    try:
        incoming_emails.insert_one(messages_add_info)
    except DuplicateKeyError:
        print(f"The message with id {messages_add_info['_id']} already exists")

pprint(len(messages_list))

for doc in incoming_emails.find({}):
    pprint(doc)

print(incoming_emails.count_documents({}))

driver.quit()
