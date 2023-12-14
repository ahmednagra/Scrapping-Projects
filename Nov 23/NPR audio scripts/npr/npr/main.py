from scrapy import cmdline

if __name__ == '__main__':
    cmdline.execute('scrapy crawl nprspider'.split())
    cmdline.execute('scrapy crawl transcript'.split())
