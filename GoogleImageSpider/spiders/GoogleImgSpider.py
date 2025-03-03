# -*- coding: utf-8 -*-
# =============================================================================
# Author: yu xunzhuang
# Date: 2025/2/26
# Copyright: 智微信科 (c) 2025
# License: Some License (e.g., MIT)
# =============================================================================
import json
from urllib.parse import urlencode, urlparse

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.exceptions import CloseSpider

from GoogleImageSpider.items import GoogleImageItem, HrefImageItem
from GoogleImageSpider.configuration import googleSettings


class GoogleImageSpider(scrapy.Spider):
    name = "GoogleImageSpider"
    domain_delay = 20
    redis_key = 'crawler:image_contextLink'
    SEARCH_QUERY = 'Bone Marrow Microscope'
    CX = googleSettings.get_cx()
    API_KEY = googleSettings.get_api_key()
    API_URL = "https://www.googleapis.com/customsearch/v1"

    def start_requests(self):
        self.logger.info("✅ Start requests triggered")
        params = {
            'q': self.SEARCH_QUERY,  # searchTerms
            'cx': self.CX,  # custom search engine ID, cx
            'key': self.API_KEY,  # API key
            'searchType': 'image',  # 指定搜索类型为图片
            'start': 1,  # startIndex
            'num': 10,  # count
            'safe': 'off',  # safe
            'inputEncoding': 'utf8',  # inputEncoding
            'outputEncoding': 'utf8'  # outputEncoding
        }
        new_url = f"{self.API_URL}?{urlencode(params)}"
        request = scrapy.Request(
            url=new_url,
            callback=self.parse,
            errback=self.handle_error,
            # meta={'params': params}
        )
        yield request

    def parse(self, response):
        # 解析 API 返回的 JSON 数据
        # 查看请求的结果
        data = json.loads(response.text)
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
            image_item['category'] = "GoogleImage"
            yield image_item

            # 发起对image_contextLink的请求
            # 根据配置文件中的DIVERGE参数，决定是否进行深度爬取
            if self.settings.get('DIVERGE'):
                context_link = item.get('image', {}).get('contextLink', '')
                if context_link:
                    yield scrapy.Request(
                        url=context_link,
                        callback=self.parse_href_images,
                        meta={'google_image_id': image_item['link']},
                        errback=self.handle_error
                    )
        # 处理分页
        if self.settings.get('NEXT_PAGE'):
            next_page = data.get('queries', {}).get('nextPage', [])
            if next_page:
                params = {
                    'q': self.SEARCH_QUERY,  # searchTerms
                    'cx': self.CX,  # custom search engine ID, cx
                    'key': self.API_KEY,  # API key
                    'searchType': 'image',  # 指定搜索类型为图片
                    'start': next_page[0].get('startIndex'),  # startIndex
                    'num': next_page[0].get('count', 10),  # count
                    'safe': 'off',  # safe
                    'inputEncoding': 'utf8',  # inputEncoding
                    'outputEncoding': 'utf8'  # outputEncoding
                }
                yield scrapy.Request(url=f"{self.API_URL}?{urlencode(params)}", callback=self.parse,
                                     errback=self.handle_error)

    def parse_href_images(self, response):
        """解析从 image_contextLink 中提取的图片及递归页面链接"""
        # 🚀 获取当前递归深度（首次调用时深度为0）
        current_depth = response.meta.get("depth", 0)
        self.logger.info(f"Processing depth {current_depth}: {response.url}")

        # 1. 提取图片资源（img标签的src）
        soup = BeautifulSoup(response.text, 'html.parser')
        for img in soup.find_all('img'):
            href_image = HrefImageItem()
            image_link = img.get('src')
            urlparse_url = urlparse(response.url)
            if 'http' not in image_link:
                image_link = f"{urlparse_url.scheme}://{urlparse_url.netloc}{image_link}"
            href_image["link"] = image_link
            href_image["image_contextLink"] = response.url
            href_image["referer"] = response.request.headers.get("Referer", b"").decode("utf-8", "ignore")
            href_image["image_height"], href_image["image_width"] = self.extract_image_dimensions(str(img))
            href_image['category'] = "HrefImage"
            yield href_image

        # 2. 提取页面超链接（a标签的href���用于递归
        if current_depth < 10:  # 🚀 控制最大深度
            for a_tag in soup.find_all('a', href=True):
                href_link = a_tag['href']
                urlparse_href = urlparse(href_link)
                if not href_link.startswith('http'):
                    href_link = f"{urlparse_href.scheme}://{urlparse_href.netloc}{href_link}"
                # 🚀 递归生成新请求，深度+1
                yield Request(
                    url=href_link,
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
