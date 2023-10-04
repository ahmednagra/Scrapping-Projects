from collections import OrderedDict

from scrapy import  Request

from .base import BaseSpider


class MmaManiaSpider(BaseSpider):
    name = 'mmamania'
    base_url = 'https://www.mmamania.com/'

    headers = {
        'authority': 'www.mmamania.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }

    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_DELAY': 2,
    }

    def start_requests(self):

        yield Request(url=self.base_url, headers=self.headers)

    def parse(self, response, **kwargs):
        articles = response.css('[data-analytics-link="article:image"]')

        for row in articles:
            url = row.css('a::attr(href)').get('')

            if not url:
                continue

            if url in self.gsheet_scraped_items_urls:
                continue

            main_image = row.css('noscript img ::attr(src)').get('') or row.css('img::attr(src)').get('')

            yield Request(url=url, headers=self.headers, callback=self.parse_detail, meta={'main_image': main_image})

    def parse_detail(self, response):
        article_url = response.url

        if article_url in self.gsheet_scraped_items_urls:
            return

        description = response.xpath("//div[@class='c-entry-content ']//*[not(ancestor::aside)]").getall()
        description = ''.join(description)[:32700]

        main_image_url = ''.join(response.css('.e-image--hero img::attr(src)').get('').split('/cdn.vox-cdn.com')[-1:])

        main_image_url = f'https://cdn.vox-cdn.com{main_image_url}' if main_image_url else response.meta.get(
            'main_image', '')

        item = OrderedDict()
        item['Title'] = response.css('.c-page-title ::text').get('').strip()
        item['Summary'] = response.css('.c-entry-summary ::text').get('')
        item['Image URL'] = main_image_url
        item['Image Text'] = response.css('.e-image--hero .e-image__meta cite ::text').get('')
        item['Description HTML'] = f'<div>{description}</div>'
        item['Published At'] = response.css('[data-ui="timestamp"] ::text').get('').strip()
        item['Article URL'] = article_url

        self.current_scraped_items.append(item)

        yield item
