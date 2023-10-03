import glob
import re
import json
from collections import OrderedDict
from datetime import datetime
from math import ceil

from scrapy import Spider, Request
from scrapy.http import XmlResponse

import xmltodict


class ChemistScraperSpider(Spider):
    name = 'chemist'
    start_urls = ['https://www.chemistwarehouse.com.au/']

    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'FEEDS': {
            f'output/Chemist Warehouse Products {datetime.now().strftime("%d%m%Y%H%M")}.csv': {
                'format': 'csv',
                'fields': ['Product URL', 'Item ID', 'Product ID', 'Brand Name', 'Product Name', 'Regular Price',
                           'Special Price', 'Short Description', 'Long Description', 'Product Information',
                           'Directions', 'Ingredients', 'SKU', 'Image URLs'],
            }
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categories_urls = self.read_cats_urls()

    def parse(self, response, **kwargs):
        categories = response.css('.category-tiles li:not(.mob-only) a::attr(href)').getall() or []

        if self.categories_urls:
            for category in self.categories_urls:
                url = self.get_category_url(category)
                yield Request(url=url, callback=self.parse_pagination)
        else:
            for category in categories:
                url = self.get_category_url(category)
                yield Request(url=url, callback=self.parse_pagination)

    def parse_pagination(self, response):
        data = self.get_json_data(response)
        total_products = data.get('universes', {}).get('universe', [{}])[0].get('items-section', {}).get('results',
                                                                                                         {}).get(
            'total-items', '')

        if not total_products:
            return

        total_products = int(total_products)
        items_per_page = 500
        total_pages = ceil(total_products / items_per_page)

        if not total_pages:
            return

        for page_number in range(1, total_pages + 1):
            start_index = (page_number - 1) * items_per_page
            url = re.sub(r'fh_start_index=\d+', f'fh_start_index={start_index}', response.url)

            yield Request(url=url, callback=self.parse_products, dont_filter=True)

    def parse_products(self, response):
        data = self.get_json_data(response)
        products = data.get('universes', {}).get('universe', [{}])[0].get('items-section', {}).get('items', {}).get(
            'item', [])

        for product in products[:10]:
            attributes = product.get('attribute', [])
            item_id = self.get_attribute(attributes, 'secondid')  # For Example  item_id = '112982'
            url = self.get_attribute(attributes, 'producturl')
            brand_name = self.get_attribute(attributes, 'brand')
            product_url = f'https://www.chemistwarehouse.com.au/webapi/products/{item_id}/details' if 'ultra-beauty' in url else url

            yield Request(url=product_url, callback=self.parse_product_detail, meta={'brand_name': brand_name})

    def parse_product_detail(self, response):
        item = OrderedDict()

        try:
            # Get json from the Ultrabeauty type products. Example: https://www.chemistwarehouse.com.au/ultra-beauty/buy/112982/
            xml = xmltodict.parse(response.text)
            ultra_beauty_product_json = xml.get('ProductDetailsModel', {})  # ulta_beauty category
            ultra_beauty_product_desc_json = ultra_beauty_product_json.get('Description', {}).get('ProductDescription',
                                                                                                  {})
        except Exception as e:
            ultra_beauty_product_json = {}
            ultra_beauty_product_desc_json = {}

        try:
            # Get JSON from page source. Will be emtpy for ultrabeauty type products
            product_page_json = json.loads(
                response.css('script[type="text/javascript"]:contains("analyticsProductData")').re_first(
                    r'({.*})').replace('\\', ''))
        except Exception as e:
            product_page_json = {}

        product_id = response.css('.product-id::text').get('').split(':')[-1]

        price = product_page_json.get('price', '') or ultra_beauty_product_json.get('Price', '')  # Current price
        was_price = response.css('.retailPrice span::text').re_first(r'[0-9.]+') or ultra_beauty_product_json.get('RRP',
                                                                                                                  '')
        item_id = ultra_beauty_product_json.get('Id', '')
        brand_name = response.meta.get('brand_name', '')
        product_name = product_page_json.get('name', '') or ultra_beauty_product_json.get('Name', '')

        item['Product URL'] = f'https://www.chemistwarehouse.com.au/ultra-beauty/buy/{item_id}/' if 'webapi' in response.url else response.url  # webapi used in the Ultrabeauty request. Example: https://www.chemistwarehouse.com.au/webapi/products/112982/details
        item['Item ID'] = product_page_json.get('id', '') or item_id
        item['Product ID'] = product_id
        item['Product Name'] = product_name
        item['Regular Price'] = was_price if was_price else price
        item['Special Price'] = price if was_price else ''
        item['Brand Name'] = self.get_brand_name(brand_name, product_name)
        item['Short Description'] = '\n\n'.join(
            [''.join(p.css('::text').getall()).strip() for p in response.css('.extended-row p')]) or ''
        item['Long Description'] = self.get_long_description(response) or self.get_ultra_beauty_long_desc(
            ultra_beauty_product_desc_json)
        item['Product Information'] = ''
        item['Directions'] = '\n'.join(
            response.css('.product-info-section.directions:contains("Directions") div ::text').getall()) or ''
        item['Ingredients'] = self.get_ingredients(response) or self.get_ultra_beauty_ingredients(
            ultra_beauty_product_desc_json)
        item['SKU'] = product_page_json.get('id', '') or ultra_beauty_product_json.get('Id', '')
        item['Image URLs'] = self.get_img_urls(response) or self.get_ultra_beauty_images(ultra_beauty_product_json)

        yield item

    def get_long_description(self, response):
        general_information = '\n'.join([x.strip() for x in response.css(
            '.product-info-section:contains("General Information") [itemprop="description"] ::text').getall()]).strip()

        warnings = '\n'.join(response.css('.product-info-section.warnings ::text').getall()).strip()
        warnings = warnings if len(warnings) > 15 else ''

        return f'{general_information}\n\n{warnings}'.strip()

    def get_ultra_beauty_long_desc(self, product_json):
        product_info = self.get_json_value_by_name(product_json, 'Product info')
        warning = self.get_json_value_by_name(product_json, 'Warnings')

        return f'{product_info}\n\n{warning}'.strip()

    def get_json_value_by_name(self, json_dict, name_text):
        return ''.join([general_info.get('Content', '') or '' for general_info in json_dict if
                        general_info.get('Name', '') == name_text]).strip()

    def get_json_data(self, response):
        try:
            return response.json() or {}
        except json.JSONDecodeError as e:
            return {}

    def get_attribute(self, attributes, value):
        return '\n'.join([url.get('value', [{}])[0].get('value') for url in attributes if url.get('name') == value])

    def get_ingredients(self, response):
        if isinstance(response, XmlResponse):
            return ''

        return '\n'.join(
            response.css('.product-info-section.ingredients:contains("Ingredients") div ::text').getall()) or ''

    def get_ultra_beauty_ingredients(self, product_json):
        ingredients = self.get_json_value_by_name(product_json, 'Ingredients')
        return ingredients

    def get_img_urls(self, response):
        if isinstance(response, XmlResponse):
            return ''

        image_urls = response.css('[u="slides"] .image_enlarger::attr(href)').getall() or response.css(
            '.empty_image::attr(src)').getall()
        return image_urls

    def get_ultra_beauty_images(self, product_json):
        product_image = product_json.get('Images', {}).get('ProductImage', [{}])
        if isinstance(product_image, list):
            image_urls = [image_dict.get('Large', '') for image_dict in product_image]
        else:
            image_urls = [product_image.get('Large', '')]

        return image_urls

    def read_cats_urls(self):
        file_name = ''.join(glob.glob('input/categories urls.txt'))
        try:
            with open(file_name, 'r') as file:
                lines = file.readlines()

            # Strip newline characters and whitespace from each line
            lines = [line.strip() for line in lines]
            return lines
        except:
            return []

    def get_category_url(self, category):
        category_id = category.split('/')[-2]  # For Example category_id = '542'
        category_format = 'chemau{category_id}'.format(category_id=category_id)
        urlp = '{catalog01_chemau}'
        return f'https://pds.chemistwarehouse.com.au/search?identifier=AU&fh_start_index=0&fh_view_size=500&fh_location=//catalog01/en_AU/categories%3C{urlp}/categories%3C{category_format}'

    def get_brand_name(self, brand_name, product_name):
        if not brand_name:
            return product_name.replace('Online Only - ', '').split()[0]

        if brand_name.lower().split()[0] not in product_name.lower():
            return product_name.replace('Online Only - ', '').split()[0]

        return brand_name
