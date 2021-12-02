# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class BookparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.labirint_ru

    def process_item(self, item, spider):
        item['_id'] = self.process_id(item['url'])

        item['name'] = self.process_name(item['name'])

        if len(item['price']) == 2:
            item['old_price'] = int(item['price'][0])
            item['new_price'] = int(item['price'][1])
        elif len(item['price']) == 1:
            item['book_price'] = int(item['price'][0])
        del item['price']

        item['rate'] = float(item['rate'])

        collection = self.mongo_base[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            print(f"The book with {item['_id']} already exists")

        return item

    def process_id(self, url):
        _id = url.split('/')[-2]
        return _id

    def process_name(self, name):
        return name.split(': ')[1]
