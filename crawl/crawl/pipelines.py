# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
import logging
from .settings import MONGODB_SERVER, MONGODB_PORT, MONGODB_DB, MONGODB_COLLECTION
from scrapy.exceptions import DropItem

logging.getLogger('pymongo').setLevel(logging.WARNING)

class CrawlPipeline:
    def __init__(self):
        connection = pymongo.MongoClient(
            MONGODB_SERVER,
            MONGODB_PORT
        )
        db = connection[MONGODB_DB]
        self.collection = db[MONGODB_COLLECTION]

    def process_item(self, item, spider):
        item = dict(item)
        data = item

        if 'post_id' in data:
            try:
                self.collection.insert_one(data)
                print("Item added to MongoDB database " + data.get('post_id'))
            except Exception as e:
                print("Error while inserting item to MongoDB database " + data.get('url'))
                print(e)
        else:
            raise DropItem(f"Missing post_id in {data.get('url')}")