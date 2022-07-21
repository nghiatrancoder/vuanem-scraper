BOT_NAME = "scraper"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 0
DOWNLOAD_TIMEOUT = 30
RANDOMIZE_DOWNLOAD_DELAY = True

REACTOR_THREADPOOL_MAXSIZE = 128
CONCURRENT_REQUESTS = 256
CONCURRENT_REQUESTS_PER_DOMAIN = 256
CONCURRENT_REQUESTS_PER_IP = 256

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 0.25
AUTOTHROTTLE_TARGET_CONCURRENCY = 128
AUTOTHROTTLE_DEBUG = True

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [
    500,
    502,
    503,
    504,
    400,
    401,
    403,
    404,
    405,
    406,
    407,
    408,
    409,
    410,
    429,
]

DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy.spidermiddlewares.referer.RefererMiddleware": 80,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 120,
    "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 130,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
    "scrapy.downloadermiddlewares.redirect.RedirectMiddleware": 900,
    "scraper.middlewares.ScraperDownloaderMiddleware": 1000,
}

FEEDS = {"export/" + "%(name)s" + ".json": {"format": "json", "overwrite": True}}
