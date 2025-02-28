# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import time
from urllib.parse import urlsplit

from scrapy import signals


# useful for handling different item types with a single interface


class GoogleimagespiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class GoogleimagespiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class DomainDelayMiddleware:
    """自定义域名请求频率控制中间件"""

    def __init__(self):
        self.domain_timestamps = {}  # 存储域名最后请求时间: {domain: timestamp}

    def process_request(self, request, spider):
        # 提取主域名（示例：从www.example.com/path提取example.com）
        domain = urlsplit(request.url).hostname

        # 检查是否需要等待
        last_request_time = self.domain_timestamps.get(domain, 0)
        current_time = time.time()
        if current_time - last_request_time < spider.domain_delay:
            wait_time = spider.domain_delay - (current_time - last_request_time)
            time.sleep(wait_time)
        # spider.logger.info(f'全局域名检查: {last_request_time}')
        # 更新域名时间戳
        self.domain_timestamps[domain] = time.time()

        return None


class GlobalProxyMiddleware:
    def process_request(self, request, spider):
        request.meta['proxy'] = 'http://127.0.0.1:7890'  # 统一代理网关
        spider.logger.info(f'正在访问: {request.url}')
        spider.logger.info(f'应用代理: {request.meta["proxy"]}')


class GlobalHeadersCookiesMiddleware:
    def process_request(self, request, spider):
        # Set global headers
        for key, value in spider.settings.get('DEFAULT_REQUEST_HEADERS').items():
            request.headers.setdefault(key, value)

        # Set global cookies
        request.cookies.update(spider.settings.get('DEFAULT_COOKIES'))
