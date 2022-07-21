import json
from urllib.parse import urlencode

from inline_requests import inline_requests

import scrapy

from scraper.items import Product, ProductVariant


class DemXinhSpider(scrapy.Spider):
    name = "DemXanh"

    root_url = "https://demxanh.com/"

    def start_requests(self):
        cotton = {"path": "dem-bong-ep", "page": range(1, 3)}
        spring = {"path": "dem-lo-xo", "page": range(1, 4)}
        latex = {"path": "dem-cao-su", "page": range(1, 3)}
        foam = {"path": "dem-foam", "page": range(1, 2)}
        cheap = {"path": "dem-gia-re", "page": range(1, 2)}

        urls = [
            self.root_url + "?" + urlencode({"page": page})
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
        product_urls = response.css('.p-item > a::attr(href)').getall()

        for url in product_urls:
            yield scrapy.Request(url, callback=self.get_product)

    @inline_requests
    def get_product(self, response):
        url = response.url
        id = response.css("#product_id::attr(value)").get()
        name = response.css("h1.title-name::text").get()
        images = response.css("#imageGallery img::attr(src)").getall()

        sizes = response.css('li[data-name="kich_thuoc"]')
        depths = response.css('li[data-name="do_day"]')

        variant_query = {
            "module": "products",
            "view": "product",
            "raw": 1,
            "task": "change_price",
        }
        variant_url = self.root_url + "?" + urlencode(variant_query)

        variants = []

        for (
            size,
            depth,
        ) in zip(sizes, depths):
            variant_response = yield scrapy.FormRequest(
                variant_url,
                formdata={
                    "id": id,
                    "extended": json.dumps(
                        {
                            "kich_thuoc": size.attrib["data-id"],
                            "do_day": depth.attrib["data-id"],
                        }
                    ),
                },
            )

            variant_data = json.loads(variant_response.text)

            variant = ProductVariant(
                size=size.attrib["data-value"],
                depth=depth.attrib["data-value"],
                price=variant_data["price"],
                sale_price=variant_data["price_new"],
            )

            variants.append(variant)

        yield Product(
            name=name,
            url=url,
            images=images,
            variants=variants,
        )
