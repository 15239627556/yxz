# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from email.policy import default

import scrapy


class GoogleImageItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()  # 图片标题
    link = scrapy.Field()  # 图片链接
    local_path = scrapy.Field() #
    htmlTitle = scrapy.Field()  # html标题
    displayLink = scrapy.Field()  # 域名
    snippet = scrapy.Field()  # 描述,摘录
    htmlSnippet = scrapy.Field()  # html摘录
    mime = scrapy.Field()  # 图片格式
    fileFormat = scrapy.Field()  # 文件格式
    image_contextLink = scrapy.Field()  # 图片的来源网页
    image_height = scrapy.Field()  # 图片高度
    image_width = scrapy.Field()  # 图片宽度
    image_byteSize = scrapy.Field()  # 图片大小
    image_thumbnailLink = scrapy.Field()  # 缩略图链接
    content_hash = scrapy.Field()
    category = scrapy.Field(default='GoogleImage')


class HrefImageItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    link = scrapy.Field()  # 图片URL
    image_contextLink = scrapy.Field()  # 来源页面URL
    local_path = scrapy.Field()
    referer = scrapy.Field()  # Referer信息
    image_height = scrapy.Field()  # 图片高度
    image_width = scrapy.Field()  # 图片宽度
    content_hash = scrapy.Field()
    category = scrapy.Field(default='HrefImage')


class DropItem(Exception):
    """自定义异常类"""
    pass
