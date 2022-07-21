import scrapy

from scraper.items import Product, ProductVariant


class TheGioiNemSpider(scrapy.Spider):
    name = "TheGioiNem"

    root_url = "https://thegioinem.com"

    def start_requests(self):
        cotton = "nem-bong-ep"
        spring = "nem-lo-xo"
        latex = "nem-cao-su"

        urls = [
            self.root_url + "/" + category
            for category in [
                cotton,
                spring,
                latex,
            ]
        ]

        for url in urls:
            yield scrapy.Request(url, callback=self.get_product_url)

    def get_product_url(self, response):
        product_urls = response.css("ul.box.load > li > a::attr(href)").getall()

        for url in product_urls:
            yield scrapy.Request(self.root_url + "/" + url, callback=self.get_product)

    def get_product(self, response):
        table = response.css('ul[name="data"] li[giaban]')

        variants = [
            ProductVariant(
                config=row.attrib["option1"],
                price=row.attrib["giacty"],
                sale_price=row.attrib["giaban"],
            )
            for row in table
        ]

        url = response.url
        name = response.css("h1.name::text").get()
        images = [
            self.root_url + "/" + href
            for href in response.css(".swiper-wrapper img::attr(src)").getall()
        ]

        yield Product(
            name=name,
            url=url,
            images=images,
            variants=variants,
        )
