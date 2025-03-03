# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import uuid
from datetime import timedelta, datetime

from pymongo import MongoClient, WriteConcern, errors
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from twisted.internet import threads, defer

from GoogleImageSpider.items import GoogleImageItem, HrefImageItem, DropItem


class HybridImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield Request(item['link'], meta={'item': item})

    def file_path(self, request, response=None, info=None, *, item=None):
        file_name = request.url.split('/')[-1]
        if '.' not in file_name:
            file_name = str(uuid.uuid4()).replace('-', '') + '.jpg'
        return f"{request.meta['item']['category']}/{file_name}"

    def item_completed(self, results, item, info):
        for ok, x in results:
            if ok:
                item['local_path'] = x['path']
        return item


class GoogleImageDownloaderPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'image_database'),
        )

    def open_spider(self, spider):
        self.client = MongoClient(
            self.mongo_uri,
            wTimeoutMS=5000,
            socketTimeoutMS=30000,
            connectTimeoutMS=30000,
            retryWrites=True,
        )
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    @defer.inlineCallbacks
    def process_item(self, item, spider):
        yield threads.deferToThread(self._process_item, item, spider)
        return item

    def _process_item(self, item, spider):
        try:
            self._sanitize_item(item)
            collection_name = self._get_collection_name(item)
            collection = self.db[collection_name].with_options(
                write_concern=WriteConcern(w='majority', j=True)
            )

            if self._is_duplicate(collection, item):
                spider.crawler.stats.inc_value('duplicate_items')
                return item

            doc = self._build_document(item)
            result = collection.insert_one(doc)

            if result.acknowledged:
                spider.logger.debug(f"插入成功 ID:{result.inserted_id}")
                spider.crawler.stats.inc_value('mongodb/insert_count')
            return item
        except errors.DuplicateKeyError as e:
            spider.logger.warn(f"重复数据: {str(e)}")
        except errors.ConnectionFailure as e:
            spider.logger.error(f"MongoDB连接失败: {str(e)}")
        except Exception as e:
            spider.logger.error(f"未知错误: {str(e)}", exc_info=True)

    def _sanitize_item(self, item):
        item['content_hash'] = hashlib.sha256(item['link'].encode()).hexdigest()

    def _build_document(self, item):
        return {
            **dict(item),
            'crawl_time': datetime.utcnow(),
            'expire_at': datetime.utcnow() + timedelta(days=30),
            '_version': '2025.1'
        }

    def _get_collection_name(self, item):
        if isinstance(item, GoogleImageItem):
            return 'google_images'
        elif isinstance(item, HrefImageItem):
            return 'href_images'
        raise DropItem("未知Item类型")

    def _is_duplicate(self, collection, item):
        return collection.count_documents({
            'content_hash': item['content_hash']
        }, limit=1) > 0
