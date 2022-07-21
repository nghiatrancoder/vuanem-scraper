import scrapy
from inline_requests import inline_requests

from scraper.items import Product, ProductVariant


class SieuThiNemSpider(scrapy.Spider):
    name = "SieuThiNem"

    root_url = "https://www.sieuthinem.vn"

    def start_requests(self):
        cotton = {"path": "nem-bong-ep", "page": range(1, 2)}
        spring = {"path": "nem-lo-xo", "page": range(1, 4)}
        latex = {"path": "nem-cao-su-chinh-hang", "page": range(1, 4)}
        folded = {"path": "nem-gap-3", "page": range(1, 2)}
        mousse = {"path": "nem-mousse", "page": range(1, 2)}

        urls = [
            f"{self.root_url}/{category['path']}.html/p-{page}"
            for category in [
                cotton,
                spring,
                latex,
                folded,
                mousse,
            ]
            for page in category["page"]
        ]

        for url in urls:
            yield scrapy.Request(url, callback=self.get_product_url)

    def get_product_url(self, response):
        product_urls = response.css(".i-image a::attr(href)").getall()

        for url in product_urls:
            yield scrapy.Request(url, callback=self.get_product)

    @inline_requests
    def get_product(self, response):
        trows = response.css('table tbody tr[height="26"]')
        variants = [
            ProductVariant(
                config=trow.css('td')[0].css('span::text').get(),
                price=trow.css('td')[1].css('span::text').get(),
                sale_price=trow.css('td')[2].css('span::text').get()
            )
            for trow in trows
        ]

        url = response.url
        name = response.css(".titleL h1::text").get()
        images = response.css('a.fancybox[rel="gallery"]::attr(href)').getall()

        yield Product(
            name=name,
            url=url,
            images=images,
            variants=variants,
        )


