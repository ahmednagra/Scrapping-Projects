import glob
import json
import time
import requests
from scrapy import Spider, Request, Selector
from collections import OrderedDict


class AphcSpider(Spider):
    name = "aphc"
    start_urls = ["https://aphc.co.uk/find-an-aphc-member/"]

    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'FEEDS': {
            f'output/Aphc Scraping Details.csv': {
                'format': 'csv',
                'fields': ['Name', 'Phone', 'E-mail', 'Address', 'Star Rating', 'Reviews', 'Business Activities',
                           'PostCode', 'URL'],
                'overwrite': True
            }
        },
    }

    headers = {
        'authority': 'aphc.co.uk',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-PK,en;q=0.9,ur-PK;q=0.8,ur;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://aphc.co.uk',
        'referer': 'https://aphc.co.uk/find-an-aphc-member/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.postcodes_from_input_file = self.read_input_postcodes()

    def start_requests(self):
        for postcode in self.postcodes_from_input_file:
            data = self.get_formdata(postcode)
            # form_data = json.dumps(data)
            # url = 'https://aphc.co.uk/member-search-results/'
            res = requests.post('https://aphc.co.uk/member-search-results/', headers=self.headers, data=data)

            # yield Request(url=url, method='POST', body=form_data, callback=self.parse, headers=self.headers)

            selector = Selector(text=res.text)
            member_urls = selector.css('.Installer-More::attr(href)').getall()

            for member_url in member_urls:
                yield Request(url=member_url, callback=self.parse, meta={'postcode': postcode})

    def parse(self, response, **kwargs):
        item = OrderedDict()
        rateing_reviews = self.get_rating_reviews(response)
        time.sleep(1)

        item['Name'] = response.css('.Individual-Wrap h2::text').get('').strip()
        item['Phone'] = response.css('.Individual-Phone::text').get('').strip()
        item['E-mail'] = response.css('.Individual-Email a::attr(href)').get('')
        item['Address'] = response.css('.Individual-Address::text').get('').strip()
        item['Star Rating'] = rateing_reviews.get('rating', '')
        item['Reviews'] = rateing_reviews.get('reviews', '').replace('reviews', '')
        item['Business Activities'] = self.get_buisness_activities(response)
        item['PostCode'] = response.meta.get('postcode', '')
        item['URL'] = response.url

        yield item

    def read_input_postcodes(self):
        file_path = ''.join(glob.glob('input/postcode.txt'))
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file.readlines()]
            return urls
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return []

    def get_formdata(self, postcode):
        data = {
            'scheme': 'Licensed Scheme',
            'postcode': postcode,
            'town': '',
            'areaOfwork': 'Residential or Commercial',
            'company': '',
            'aphcMemberSearchButton': 'Search',
        }

        return data

    def get_rating_reviews(self, response):
        map_url = response.css('.Individual-Col-8 iframe::attr(src)').get('')

        def convert_to_dict(lst):
            if isinstance(lst, list):
                return {str(i): convert_to_dict(item) for i, item in enumerate(lst)}
            return lst

        try:
            res = requests.get(url=map_url)
            selector = Selector(text=res.text)
            string = selector.css('script:contains("onEmbedLoad")::text').extract_first().strip()

            start_point = 'initEmbed('
            end_point = 'function onApiLoad()'
            start_index = string.find(start_point) + len(start_point)
            end_index = string.find(end_point)

            new_string = string[start_index:end_index]
            new_string = new_string.strip().split(';')[0].replace(')', '')
            new_list = json.loads(new_string)

            nested_dict = convert_to_dict(new_list)

            review_dict = nested_dict.get('21', {}).get('3', {})
            review = review_dict.get('4', '') if review_dict is not None else ''
            review = '' if review is None else review

            if 'reviews' in review:
                review = review.replace('reviews', '')


            rating_dict = nested_dict.get('21', {}).get('3', {})
            rating = rating_dict.get('3', '') if rating_dict is not None else ''
            rating = '' if rating is None else rating

            if rating:
                float_rating = float(rating)
                if float_rating % 1 != 0:  # Checks if it's a decimal value
                    decimal_length = len(str(float_rating).split(".")[1])
                    if decimal_length > 2:  # Check if the decimal part has more than 2 digits
                        rating = "{:.4f}".format(float_rating)

            data_dict = {
                    'reviews': review,
                    'rating': rating
                }

            return data_dict

            # if string:
            #     reviews = ''.join([x for x in string.split(',') if 'reviews' in x]).replace('"', '')
            #
            #     rating = ''
            #     split_values = string.split(',')
            #
            #     for idx, x in enumerate(split_values):
            #         if 'reviews' in x:
            #             rating = split_values[idx - 1]
            #             # Truncate the string to four decimal places
            #             rating = "{:.4f}".format(float(rating))
            #             break
            #
            #     data_dict = {
            #         'reviews': reviews,
            #         'rating': rating
            #     }
            #
            #     return data_dict

        except Exception as e:
            print(f"An error occurred: {e}")
            return {'reviews': '', 'rating': ''}

    def get_buisness_activities(self, response):
        buisness_activities = []
        selectors = response.css('.Individual-Cat')
        for selector in selectors:
            activities = ' '.join(selector.css('.Individual-Icon-Title ::text').getall())
            buisness_activities.append(activities)

        return ', '.join(buisness_activities)
