import json

import scrapy

from scraper.items import Product, ProductVariant


class KinhDoDem(scrapy.Spider):
    name = "KinhDoDem"

    root_url = "https://kinhdonem.com"

    def start_requests(self):
        cotton = "nem-bong-ep"
        spring = "nem-lo-xo"
        latex = "nem-cao-su-thien-nhien"
        latex_massage = "nem-cao-su-thien-nhien-massage"
        hotel = "nem-hotel"
        homestay = "san-pham-khach-san/nem-homestay-nha-nghi"

        urls = [
            f"{self.root_url}/{category}"
            for category in [
                cotton,
                spring,
                latex,
                latex_massage,
                hotel,
                homestay,
            ]
        ]

        for url in urls:
            yield scrapy.Request(url, callback=self.get_product_url)

    def get_product_url(self, response):
        product_urls = response.css(".image-zoom > a::attr(href)").getall()

        for url in product_urls:
            yield scrapy.Request(url, callback=self.get_product)

    def get_product(self, response):
        form = response.css("form.variations_form::attr(data-product_variations)").get()

        try:
            variant_data = json.loads(form)

            variants = [
                ProductVariant(
                    config=variant["attributes"]["attribute_pa_kich-thuoc"],
                    price=variant["display_regular_price"],
                    sale_price=variant["display_price"],
                )
                for variant in variant_data
            ]
        except TypeError:
            variants = []

        url = response.url
        name = response.css("h1.product-title::text").get()
        images = response.css(
            "img.attachment-woocommerce_thumbnail::attr(src)"
        ).getall()

        yield Product(
            name=name,
            url=url,
            images=images,
            variants=variants,
        )
