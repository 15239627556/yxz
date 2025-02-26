# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


import requests
from pymongo import MongoClient

from GoogleImageSpider.items import GoogleImageItem, HrefImageItem, DropItem
import os


class GoogleImageDownloaderPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        # 从 settings.py 中获取 MongoDB 配置
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'image_scraper')
        )

    def open_spider(self, spider):
        # 连接 MongoDB
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        # 关闭 MongoDB 连接
        self.client.close()

    def process_item(self, item, spider):

        """处理 Item 数据"""
        if isinstance(item, GoogleImageItem):
            collection = self.db['google_images']
            save_dir = 'google_images'
        elif isinstance(item, HrefImageItem):
            collection = self.db['href_images']
            save_dir = 'href_images'
        else:
            raise DropItem("未知的 Item 类型")
        # 下载图片
        image_url = item['link']
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        image_name = image_url.split('/')[-1]
        save_path = os.path.join(save_dir, image_name)

        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                item['local_path'] = save_path
                print(f'图片下载成功: {save_path}')
            else:
                print(f'图片下载失败，状态码: {response.status_code}')
        except Exception as e:
            print(f'下载图片时出错: {e}')
            return item

        # 存储到 MongoDB
        try:
            collection.insert_one(dict(item))
            print(f'图片信息已存储到 MongoDB: {item["title"]}')
        except Exception as e:
            print(f'存储到 MongoDB 时出错: {e}')

        return item
