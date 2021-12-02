import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/genres/2542/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='pagination-next__text']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        main_link = 'https://www.labirint.ru'
        links = response.xpath("//div[@data-title='Все в жанре «Зарубежное фэнтези»']//a[@class='product-title-link']/@href").getall()
        for link in links:
            yield response.follow(main_link + link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        author = response.xpath("//div[@class='authors']/a/text()").get()
        price = response.xpath("//span[contains(@class, 'val-number')]/text()").getall()
        rate = response.xpath("//div[@id='rate']/text()").get()
        url = response.url
        yield BookparserItem(name=name, author=author, price=price, rate=rate, url=url)
