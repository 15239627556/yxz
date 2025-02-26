# -*- coding: utf-8 -*-
# =============================================================================
# Author: yu xunzhuang
# Date: 2025/2/26
# Copyright: 智微信科 (c) 2025
# License: Some License (e.g., MIT)
# =============================================================================
import json
import time

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlencode
print(f'scrapy_version: {scrapy.__version__}')

from GoogleImageSpider.items import GoogleImageItem, HrefImageItem


class GoogleImageSpider(scrapy.Spider):
    name = "googleImageSpider"  # 爬虫名称
    allowed_domains = ['googleapis.com', 'baidu.com']  # 允许爬取的域名
    domain_delay = 20  # 同一域名请求间隔时间
    redis_key = 'crawler:image_contextLink'  # Redis任务队列键名
    SEARCH_QUERY = '红细胞'  # 搜索关键词
    cx = '260207ac67ef144f4'  # 替换为你的Custom Search ID
    api_key = 'AIzaSyDbOd586kF3mt1GmpBP3_T84Q01a0E-x1o'  # 替换为你的API密钥

    # custom_settings = {
    #     'DUPEFILTER_CLASS': 'scrapy_redis.dupefilter.RFPDupeFilter',
    #     'SCHEDULER': 'scrapy_redis.scheduler.Scheduler',
    #     'REDIS_URL': 'redis://localhost:6379',
    #     'MONGODB_URI': 'mongodb://localhost:27017',
    #     'MONGODB_DB': 'image_scraper',
    #     'LOG_LEVEL': 'INFO',
    #     'DOWNLOAD_DELAY': 20,
    #     'AUTOTHROTTLE_ENABLED': True,
    #     'RETRY_ENABLED': True,
    #     'RETRY_TIMES': 5,
    #     'RETRY_HTTP_CODES': [400, 403, 408, 429, 500, 502, 503, 504],
    # }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # self.NUM_RESULTS = 10  # 获取的图片数量
    #     self.SEARCH_QUERY = '红细胞'  # 搜索关键词
    #     self.cx = '260207ac67ef144f4'  # 替换为你的Custom Search ID
    #     self.api_key = 'AIzaSyDbOd586kF3mt1GmpBP3_T84Q01a0E-x1o'  # 替换为你的API密钥

    def start_requests(self):
        self.logger.info("✅ Start requests triggered")
        api_url = "https://www.googleapis.com/customsearch/v1?"
        params = {
            'q': self.SEARCH_QUERY,  # searchTerms
            'cx': self.cx,  # custom search engine ID, cx
            'key': self.api_key,  # API key
            'searchType': 'image',  # 指定搜索类型为图片
            'start': 1,  # startIndex
            'num': 10,  # count
            'safe': 'off',  # safe
            'inputEncoding': 'utf8',  # inputEncoding
            'outputEncoding': 'utf8'  # outputEncoding
        }
        # url = api_url + urlencode(params)
        url = 'https://www.baidu.com'
        request = scrapy.Request(url=url, callback=self.parse_href_images, errback=self.handle_error)
        # self.crawler.signals.connect(
        #     lambda response: self.logger.debug(f"🔥 Signal: {response.status} from {response.url}"),
        #     signal=scrapy.signals.response_received
        # )
        self.logger.info(f"✅ Start requests triggered: {url}")
        yield request

    def parse(self, response):
        print(1111)
        # 解析 API 返回的 JSON 数据
        data = json.loads(response.text)
        print(data)
        for item in data.get('items', []):
            image_item = GoogleImageItem()
            image_item['title'] = item.get('title')
            image_item['link'] = item.get('link')
            image_item['htmlTitle'] = item.get('htmlTitle')
            image_item['displayLink'] = item.get('displayLink')
            image_item['snippet'] = item.get('snippet')
            image_item['htmlSnippet'] = item.get('htmlSnippet')
            image_item['mime'] = item.get('mime')
            image_item['fileFormat'] = item.get('fileFormat')
            image_item['image_contextLink'] = item.get('image', {}).get('contextLink')
            image_item['image_height'] = item.get('image', {}).get('height')
            image_item['image_width'] = item.get('image', {}).get('width')
            image_item['image_byteSize'] = item.get('image', {}).get('byteSize')
            image_item['image_thumbnailLink'] = item.get('image', {}).get('thumbnailLink')
            yield image_item

            # 发起对image_contextLink的请求
            context_link = item.get('image', {}).get('contextLink', '')
            if context_link:
                yield scrapy.Request(
                    url=context_link,
                    callback=self.parse_href_images,
                    meta={'google_image_id': image_item['link']},
                    errback=self.handle_error
                )
        # 先注释掉
        # 处理分页
        # next_page = data.get('queries', {}).get('nextPage', [])
        # if next_page:
        #     api_url = "https://www.googleapis.com/customsearch/v1?"
        #     params = {
        #         'q': self.SEARCH_QUERY,  # searchTerms
        #         'cx': self.cx,  # custom search engine ID, cx
        #         'key': self.api_key,  # API key
        #         'searchType': 'image',  # 指定搜索类型为图片
        #         'start': next_page[0].get('startIndex', 1),  # startIndex
        #         'num': next_page[0].get('count', 10),  # count
        #         'safe': 'off',  # safe
        #         'inputEncoding': 'utf8',  # inputEncoding
        #         'outputEncoding': 'utf8'  # outputEncoding
        #     }
        #     yield scrapy.FormRequest(url=api_url + urlencode(params), callback=self.parse, errback=self.handle_error)

    def parse_href_images(self, response):
        """解析从 image_contextLink 中提取的图片及递归页面链接"""
        # 🚀 获取当前递归深度（首次调用时深度为0）
        current_depth = response.meta.get("depth", 0)
        self.logger.info(f"Processing depth {current_depth}: {response.url}")

        # 1. 提取图片资源（img标签的src）
        img_extractor = LinkExtractor(tags="img", attrs="src")
        for link in img_extractor.extract_links(response):
            href_image = HrefImageItem()
            href_image["link"] = link.url
            href_image["image_contextLink"] = response.url
            href_image["referer"] = response.request.headers.get("Referer", b"").decode("utf-8", "ignore")
            # 🚀 优化尺寸提取逻辑（建议异步下载图片头信息）
            href_image["image_height"], href_image["image_height"] = self.extract_image_dimensions(link.text)
            yield href_image

        # 2. 提取页面超链接（a标签的href）用于递归
        if current_depth < 10:  # 🚀 控制最大深度
            page_extractor = LinkExtractor(
                tags="a",
                attrs="href",
                allow=(r"\.html$", r"\.php$"),  # 示例：仅跟踪网页类型链接
                deny_domains=("ads.com",)  # 排除广告域名
            )
            for link in page_extractor.extract_links(response):
                # 🚀 递归生成新请求，深度+1
                yield Request(
                    url=link.url,
                    callback=self.parse_href_images,
                    meta={
                        "depth": current_depth + 1,  # 🚀 传递深度参数
                        "referer": response.url
                    },
                    priority=10 - current_depth  # 深度越大优先级越低
                )

    def extract_image_dimensions(self, img_tag):
        """从img标签中提取尺寸信息（示例）"""
        # 示例：src="image.jpg" width="300" height="200"
        width = self.extract_attr(img_tag, 'width')
        height = self.extract_attr(img_tag, 'height')
        return width, height

    def extract_attr(self, tag, attr):
        """从HTML标签中提取属性值"""
        import re
        match = re.search(f'{attr}="([^"]+)"', tag)
        return match.group(1) if match else None

    def handle_error(self, failure):
        """处理请求失败的情况"""
        print('关闭close_spider')
        self.logger.info('error: 关闭close_spider')
        self.logger.error(f"Request failed: {failure}")
        # 切换代理
        self.crawler.engine.close_spider(self, "Proxy error")
        raise CloseSpider("Proxy error")