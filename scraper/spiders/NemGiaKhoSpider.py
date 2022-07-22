import json
from urllib.parse import urlencode
from itertools import product

from inline_requests import inline_requests

import scrapy

from scraper.items import Product, ProductVariant


class NemGiaKhoSpider(scrapy.Spider):
    name = "NemGiaKho"

    root_url = "https://nemgiakho.com"

    def start_requests(self):

        cotton = "nem-bong-ep"
        spring = "nem-lo-xo"
        latex = "nem-cao-su"

        urls = [
            f"{self.root_url}/{category}"
            for category in [
                cotton,
                spring,
                latex,
            ]
        ]

        for url in urls:
            yield scrapy.Request(url, callback=self.get_product_url)

    def get_product_url(self, response):
        product_urls = response.css(".listsp a::attr(href)").getall()

        for url in product_urls:
            yield scrapy.Request(f"{self.root_url}/{url}", callback=self.get_product)

    @inline_requests
    def get_product(self, response):
        id = response.css("#ProductId::attr(value)").get()

        sizes = response.css(".listsize > option")
        areas = response.css(".listarea > option")

        variant_url = f"{self.root_url}/action.php"

        variants = []

        for size, area in product(sizes, areas):
            variant_response = yield scrapy.FormRequest(
                variant_url,
                formdata={
                    "action": "updatepriceweb",
                    "id": id,
                    "size": size.attrib["value"],
                    "area": area.attrib["value"],
                },
            )

            variant = ProductVariant(
                config=str(size.css("::text").get())
                + "-"
                + str(area.css("::text").get()),
                price=variant_response.css(".giacty::text").get(),
                sale_price=variant_response.css(".giaban::text").get(),
            )

            variants.append(variant)

        url = response.url
        name = response.css(".product > h1::text").get()
        images = response.css(".item > img::attr(src)").getall()

        yield Product(
            name=name,
            url=url,
            images=images,
            variants=variants,
        )
