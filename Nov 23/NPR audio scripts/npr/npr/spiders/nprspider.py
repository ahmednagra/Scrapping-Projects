import os
import re
import glob
import json
from urllib.parse import urljoin
from collections import OrderedDict

import requests

from scrapy import Spider, Request


class NprSpider(Spider):
    name = "nprspider"
    start_urls = ["https://www.npr.org/"]

    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'FEEDS': {
            f'output/NPR Articles Details.csv': {
                'format': 'csv',
                # 'fields': ['Title', 'Article Id', 'Date', 'Category', 'Sub Category', 'Sub Sub Category','Sub Sub Sub Category', 'Summary', 'URL'],
                'fields': ['Title', 'Article Id', 'Date', 'Category', 'Has Audio', 'Summary', 'URL'],
                'overwrite': True
            }
        },
    }

    def parse(self, response, **kwargs):
        categories = response.css(
            'ul.menu__list .menu__item--news, .menu__item--culture, .menu__item--music, .menu__item--shows-podcasts')
        for subcategories in categories:
            url = subcategories.css('.menu__item-inner a::attr(href)').get('')
            url = urljoin(self.start_urls[0], url)
            category_name = subcategories.css('.menu__item-inner a::text').get('')
            print('Category Name:', category_name)
            yield Request(url=url, callback=self.parse_categories, meta={'category_name': category_name})

    def parse_categories(self, response):
        if 'podcasts-and-shows' in response.url:
            selectors = response.css('.agglocation.category-list')
            for selector in selectors:
                playlist_items = selector.css('.bucketwrap.internallink')
                response.meta['subcategory_name'] = selector.css('.conheader ::text').get('')
                print('Podcost Subcategory Name :', selector.css('.conheader ::text').get(''))
                for item in playlist_items:
                    url = item.css('.directory-item__link ::attr(href)').get('')
                    yield Request(url=url, callback=self.parse_subcategories, meta=response.meta)

        # News and Culture Subcategories
        subcategories = response.css('.subnav-tools-wrap .animated.fadeInRight li')
        # Music Subcategories
        subcategories = subcategories or response.css('.menu__list.menu__list--ecosystem.menu__list--music li:not(.menu__item--music-home)')
        for subcategory in subcategories:
            url = subcategory.css('a::attr(href)').get('')
            joinurl = urljoin(base=self.start_urls[0], url=url)
            response.meta['subcategory_name'] = subcategory.css('a::text').get('').strip()
            print(f'category {response.meta.get("category_name", "")} and Subcategory Name :', subcategory.css('a::text').get('').strip())
            yield Request(url=joinurl, callback=self.parse_subcategories, meta=response.meta)

    def parse_subcategories(self, response):
        if not 'article' in response.text:
            return

        # if more subcategories founded News and culture categories
        more_subcategoreis = response.css('.subnav-tools-wrap .animated.fadeInRight li')
        if more_subcategoreis:
            for subcategory in more_subcategoreis:
                url = subcategory.css('a::attr(href)').get('')
                modified_url = urljoin(base=self.start_urls[0], url=url)
                print('more Categories url :', modified_url)
                if response.meta.get('sub subcategory_name', ''):
                    response.meta['sub sub subcategory_name'] = subcategory.css('a::text').get('').strip()
                else:
                    response.meta['sub subcategory_name'] = subcategory.css('a::text').get('').strip()

                print('More Subcategory Name :', subcategory.css('a::text').get('').strip())
                yield Request(url=modified_url, callback=self.parse_subcategories, meta=response.meta)

        else:

            try:
                pre_subcategory_name = response.meta.get('subcategory_name', '')
                if not pre_subcategory_name:
                    response.meta['subcategory_name'] = response.css('.branding__title b::text').get('') or response.css(
                        '.branding__title::text').get('')

                # Podcasts & Shows category
                article_selectors = response.css('article.rundown-segment')
                # News, Culture, Sub Categories and next page  Articles
                article_selectors = article_selectors or response.css(
                    '#main-section #overflow article.item') or response.css('div article.item')

                for article in article_selectors:
                    # News, Sub Category and next page Article url
                    article_url = article.css('.teaser a::attr(href)').get('') or article.css('h2.title a::attr(href)').get('')
                    # Podcasts & Shows subcategory article urls
                    article_url = article_url or article.css('h3 a::attr(href)').get('')

                    if article_url:
                        url = urljoin(self.start_urls[0], article_url)
                        print('Article url for Detail page :', url)
                        yield Request(url=url, callback=self.parse_article_details, meta=response.meta)
                    else:
                        return

            except Exception as e:
                print('Error in parse_subcategories:', e)
                return

        # request call back with condition for pagination
        next_page = response.css('.options__load-more').get('')
        page_num = 1

        # next page selector on only first page subcategory.
        if next_page and page_num == 1:
            story_id = re.search(r'(NPR.serverVars = {.*})', response.css('script#npr-vars::text').get(''))

            if story_id:
                story_id_json = story_id.group(1).replace('NPR.serverVars = ', '')
                subcategory_id = json.loads(story_id_json).get('storyId', '')
            else:
                subcategory_id = response.css('link[rel="alternate"] ::attr(href)').getall()[1].split('/')[3]

            page_num += 1
            response.meta['start_from'] = 24
            url = f'https://www.npr.org/get/{subcategory_id}/render/partial/next?start=24'

        else:
            prev_start_from = response.meta.get('start_from', '')

            # podcost subcategories playlist detail page because these categories no More load products
            if not prev_start_from:
                return

            next_start_from = prev_start_from + 24
            url = response.url.replace(f'start={prev_start_from}', f'start={next_start_from}')
            response.meta['start_from'] = next_start_from

        yield Request(url=url, callback=self.parse_subcategories, meta=response.meta)

    def parse_article_details(self, response):
        if response.css('.list-overflow'):
            articles = response.css('.list-overflow article.item')
            for article in articles:
                item = self.get_items(article, response)
                yield item

        else:
            item = OrderedDict()
            title = response.css('.storytitle h1::text').get('')
            if not title:
                return

            article_id = self.get_story_id(response)
            podcast_url = response.css('.audio-tool-download a::attr(href)').get('')
            download_podcost = self.download_podcost_audio_file(article_id, podcast_url, response)
            item['Title'] = title
            item['Article Id'] = article_id
            item['Date'] = response.css('.dateblock .date::text').get('').replace('Updated', '').strip()
            item['Category'] = response.meta.get('category_name', '')
            item['Has Audio'] = 'True' if podcast_url else 'False'
            item['Sub Category'] = response.meta.get('subcategory_name', '')
            item['Sub Sub Category'] = response.meta.get('sub subcategory_name', '')
            item['Sub Sub Sub Category'] = response.meta.get('sub sub subcategory_name', '')
            item['Summary'] = response.css('.storytext.storylocation.linkLocation p::text').get('').strip()
            item['URL'] = response.url

            yield item

    def download_podcost_audio_file(self, article_id, podcost_url, response):
        if not podcost_url:
            return False

        output_directory = 'output/audio'
        if not os.path.isdir(output_directory):
            os.mkdir(output_directory)

        file_path = f'{os.path.join(output_directory, article_id)}.mp3'

        try:
            if article_id in [x.split('\\')[-1].split('.')[0] for x in glob.glob('output/audio/*')]:
                print(f'File {article_id} Already Exists')
                return True

            else:
                print(f'File {article_id} Downloading is started.')
                res = requests.get(url=podcost_url)
                res.raise_for_status()

                with open(file_path, 'wb') as f:
                    f.write(res.content)

                print(f'File {article_id} saved successfully.')
                return True

        except requests.RequestException as e:
            print(' podcast_url: ', podcost_url)
            print('Article url:', response.url)
            print(f'Error downloading file {article_id}: {e}')
            return False

    def get_items(self, article, response):
        item = OrderedDict()

        title = article.css('.title a::text').get('')
        if not title:
            return

        article_id = self.get_story_id(article)
        article_url = article.css('.title a::attr(href)').get('')
        podcost_url = article.css('.audio-tool.audio-tool-download a::attr(href)').get('')
        download_podcost = self.download_podcost_audio_file(article_id, podcost_url, response)
        item['Title'] = title
        item['Article Id'] = article_id
        date = article.css('.dateblock .date::text').get('')
        date = date or article.css('time::attr(datetime)').get('')
        item['Date'] = date.replace('Updated', '').strip()
        item['Category'] = response.meta.get('category_name', '')
        item['Has Audio'] = 'True' if podcost_url else 'False'
        item['Sub Category'] = response.meta.get('subcategory_name', '')
        item['Sub Sub Category'] = response.meta.get('sub subcategory_name', '')
        item['Sub Sub Sub Category'] = response.meta.get('sub sub subcategory_name', '')
        summary = article.css('.storytext.storylocation.linkLocation p::text').get('').strip()
        summary = summary or article.css('.teaser a::text').get('').strip()
        # Music Category and subcategories summary
        summary = (summary or ''.join([x.strip() for x in article.css('p.teaser::text').getall()])
                   .strip()) if article.css('p.teaser::text').get('') else ''
        item['Summary'] = summary
        item['URL'] = article_url

        return item

    def get_story_id(self, response):
        story_id = re.search(r'(NPR.serverVars = {.*})', response.css('script#npr-vars::text').get(''))
        podcost_audio = response.css('.audio-module-tools-toggle').get('')

        if story_id:
            story_id_json = story_id.group(1).replace('NPR.serverVars = ', '')
            subcategory_id = json.loads(story_id_json).get('storyId', '')
        elif podcost_audio:
            subcategory_id = podcost_audio.split('storyId')[1].split(',')[0].replace(':', '').replace('"', '')
        else:
            subcategory = response.css('.title a::attr(href)').get('')
            subcategory_id = subcategory.split('/')[6] if subcategory else 'No Id exist'

        # return subcategory_id if subcategory_id else "No Id Found"
        return subcategory_id
