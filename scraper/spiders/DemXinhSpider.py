import json
from urllib.parse import urlencode
from itertools import product

import scrapy
from inline_requests import inline_requests

from scraper.items import Product, ProductVariant


class DemXinhSpider(scrapy.Spider):
    name = "DemXinh"

    root_url = "https://demxinh.vn"

    def start_requests(self):

        cotton = {"cid": 172, "page": range(1, 3)}
        spring = {"cid": 169, "page": range(1, 4)}
        latex = {"cid": 171, "page": range(1, 3)}
        foam = {"cid": 170, "page": range(1, 3)}

        default_query = {
            "module": "products",
            "view": "cat",
            "task": "loadProductsPage",
            "raw": 1,
        }

        qss = [
            urlencode(
                {
                    **default_query,
                    "cid": category["cid"],
                    "page": page,
                }
            )
            for category in [
                cotton,
                spring,
                latex,
                foam,
            ]
            for page in category["page"]
        ]

        urls = [
            f"{self.root_url}/?{qs}"
            for qs in qss
        ]

        for url in urls:
            yield scrapy.Request(url, callback=self.get_product_url)

    def get_product_url(self, response):
        product_urls = response.css("h3.frame_title > a::attr(href)").getall()

        for url in product_urls:
            yield scrapy.Request(url, callback=self.get_product)

    @inline_requests
    def get_product(self, response):
        id = response.css("#product_id::attr(value)").get()

        sizes = response.css('li[data-name="kich_thuoc"]')
        depths = response.css('li[data-name="do_day"]')

        variant_query = {
            "module": "products",
            "view": "product",
            "raw": 1,
            "task": "change_price",
        }
        variant_url = f"{self.root_url}/?{urlencode(variant_query)}"

        variants = []

        for (
            size,
            depth,
        ) in product(sizes, depths):
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
                config=size.attrib["data-value"] + "-" + depth.attrib["data-value"],
                price=variant_data["price"],
                sale_price=variant_data["price_new"],
            )

            variants.append(variant)

        url = response.url
        name = response.css("h1.title-name::text").get()
        images = response.css("#imageGallery img::attr(src)").getall()

        yield Product(
            name=name,
            url=url,
            images=images,
            variants=variants,
        )
