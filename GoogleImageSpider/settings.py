# Scrapy settings for GoogleImageSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "GoogleImageSpider"

SPIDER_MODULES = ["GoogleImageSpider.spiders"]
NEWSPIDER_MODULE = "GoogleImageSpider.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "GoogleImageSpider (+http://www.yourdomain.com)"

# 启动命令
# scrapy crawl GoogleImageSpider -s JOBDIR=crawls/GoogleImageSpider-1

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# href发散设置开关
DIVERGE = False
# NEXT_PAGE
NEXT_PAGE = False

# 日志级别
LOG_LEVEL = 'INFO'
# LOG_FILE = 'scrapy.log'

# MONGO 配置
import pymongo

MONGO_URI = 'mongodb://172.18.100.163:27017'
MONGO_DATABASE = 'image_database'
MONGO_INDEXES = {  # 自动创建索引
    'google_images': [('link', pymongo.ASCENDING)],
    'href_images': [('link', pymongo.ASCENDING)]
}

# 启用Redis的DupeFilter和Scheduler
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
# SCHEDULER = 'scrapy_redis.scheduler.Scheduler'

# Redis连接配置
REDIS_URL = 'redis://localhost:6379'  # Redis服务器地址和端口
REDIS_DB = 0  # Redis数据库编号（默认为0）

# 允许请求队列在爬虫关闭时保留
# SCHEDULER_PERSIST = True


# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 20
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# Set default request headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

# Define global cookies
DEFAULT_COOKIES = {
    'Cookie': 'example_cookie_value'
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "GoogleImageSpider.middlewares.GoogleimagespiderSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "GoogleImageSpider.middlewares.GlobalProxyMiddleware": 100,
    "GoogleImageSpider.middlewares.DomainDelayMiddleware": 543,
    "GoogleImageSpider.middlewares.GlobalHeadersCookiesMiddleware": 600,
}

# 启用并设置Pipeline执行顺序（数值越小优先级越高）
ITEM_PIPELINES = {
    'GoogleImageSpider.pipelines.HybridImagePipeline': 200,
    'GoogleImageSpider.pipelines.GoogleImageDownloaderPipeline': 300,

}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "GoogleImageSpider.pipelines.GoogleimagespiderPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
