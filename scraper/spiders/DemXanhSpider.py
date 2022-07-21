from urllib.parse import urlencode

import scrapy
import chompjs

from scraper.items import Product, ProductVariant


class DemXanhSpider(scrapy.Spider):
    name = "DemXanh"

    root_url = "https://demxanh.com"

    def start_requests(self):
        cotton = {"path": "dem-bong-ep", "page": range(1, 3)}
        spring = {"path": "dem-lo-xo", "page": range(1, 4)}
        latex = {"path": "dem-cao-su", "page": range(1, 3)}
        foam = {"path": "dem-foam", "page": range(1, 2)}
        cheap = {"path": "dem-gia-re", "page": range(1, 2)}

        urls = [
            self.root_url
            + "/"
            + category["path"]
            + ".html?"
            + urlencode({"page": page})
            for category in [
                cotton,
                spring,
                latex,
                foam,
                cheap,
            ]
            for page in category["page"]
        ]

        for url in urls:
            yield scrapy.Request(url, callback=self.get_product_url)

    def get_product_url(self, response):
        product_urls = response.css(".p-item > a::attr(href)").getall()

        for url in product_urls:
            yield scrapy.Request(self.root_url + url, callback=self.get_product)

    def get_product(self, response):
        script = response.css('script:contains("var product_config_count")::text').get()
        js_objects = chompjs.parse_js_object(script)

        variant_list = js_objects["variant_list"]
        product_info = js_objects["product_info"]

        variants = [
            ProductVariant(
                config=variant['sku'],
                price=variant["extend"]["market_price"],
                sale_price=variant["sale_price"],
            )
            for variant in variant_list
        ]

        url = response.url
        name = product_info["label"]
        images = [
            self.root_url + href
            for href in response.css('a[data-fancybox="gallery"]::attr(href)').getall()
        ]

        yield Product(
            name=name,
            url=url,
            images=images,
            variants=variants,
        )
