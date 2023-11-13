import glob
import json
import time
import requests
from scrapy import Spider, Request, Selector
from collections import OrderedDict


class BooksSpider(Spider):
    name = "books"
    start_urls = ["https://www.awesomebooks.com/books/bestsellers"]

    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'FEEDS': {
            f'output/Awesome Books Scraping Details.csv': {
                'format': 'csv',
                'fields': ['Title', 'Author', 'Full Price', 'Discount Price', 'Discounted Amount', 'ISBN', 'URl'],
                'overwrite': True
            }
        },
    }

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse)

    def parse(self, response, **kwargs):
        item = OrderedDict()
        books_selector = response.css('.row.list-unstyled.products-group.no-gutters li')
        for book in books_selector:
            item['Title'] = book.css('.book_title a::text').get('')
            item['Author'] = book.css('.book_author a::text').get('')
            item['Full Price'] = book.css('.rrp ::text').get('')
            item['Discount Price'] = book.css('.product-price span:not(.rrp) ::text').get('')
            item['Discounted Amount'] = book.css('.rrp.text-primary ::text').get('').replace('Save', '').strip()
            item['ISBN'] = book.css('[rel="nofollow"]::attr(data-isbn)').get('')
            item['URl'] = book.css('.d-block::attr(href)').get('')

            yield item
