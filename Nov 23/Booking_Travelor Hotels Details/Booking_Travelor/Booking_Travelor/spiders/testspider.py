import json
import re
import time
from math import ceil
from time import sleep

import requests
from collections import OrderedDict
from scrapy import Spider, Request


class SNOSpider(Spider):
    name = 'sno'
    start_urls = ['https://sno2023.eventscribe.net/agenda.asp?pfp=days']

    def parse(self, response, **kwargs):
        a=1