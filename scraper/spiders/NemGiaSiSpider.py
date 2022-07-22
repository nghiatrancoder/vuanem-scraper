import json

import scrapy
from inline_requests import inline_requests

from scraper.items import Product, ProductVariant


class NemGiaSiSpider(scrapy.Spider):
    name = "NemGiaSi"

    root_url = "https://nemgiasi.vn"

    def start_requests(self):

        cotton = "nem-bong-ep"
        spring = "nem-lo-xo"
        latex = "nem-cao-su"
        foam = "nem-cao-su-khoa-hoc"
        pe = "nem-pe"
        baby = "nem-em-be"

        urls = [
            f"{self.root_url}/{category}"
            for category in [
                cotton,
                spring,
                latex,
                foam,
                pe,
                baby,
            ]
        ]

        for url in urls:
            yield scrapy.Request(url, callback=self.get_product_url)

    def get_product_url(self, response):
        product_urls = response.css(".img-pro a::attr(href)").getall()

        for url in product_urls:
            yield scrapy.Request(f"{self.root_url}/{url}", callback=self.get_product)

    @inline_requests
    def get_product(self, response):
        sizes = response.css("#size-product > option")

        variant_url = f"{self.root_url}/ajax/ajax_price_size.php"

        variants = []

        for size in sizes:
            variant_response = yield scrapy.FormRequest(
                variant_url,
                formdata={
                    "id": size.attrib["value"],
                },
            )

            variant_data = json.loads(variant_response.text)

            variant = ProductVariant(
                config=str(size.css("::text").get()),
                price=variant_data["gia"],
                sale_price=variant_data["giagiam"],
            )

            variants.append(variant)

        url = response.url
        name = response.css("p.title-pro-detail::text").get()
        images = response.css("a.thumb-pro-detail > img::attr(src)").getall()

        yield Product(
            name=name,
            url=url,
            images=[f"{self.root_url}/{image}" for image in images],
            variants=variants,
        )
