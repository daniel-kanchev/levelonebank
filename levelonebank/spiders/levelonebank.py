import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from levelonebank.items import Article


class levelonebankSpider(scrapy.Spider):
    name = 'levelonebank'
    start_urls = ['https://www.levelonebank.com/Resources/Learning-Center/Blog']

    def parse(self, response):
        links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="page"]/@href').getall()
        yield from response.follow_all(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('(//h1)[2]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="meta_text no_margin"]/text()').get()
        if date:
            date = " ".join(date.split()[2:])

        content = response.xpath('//div[@class="main_content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
