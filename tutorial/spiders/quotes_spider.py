import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    def parse(self, response):

        print('CAPTCHAR_RETRY_TIMES is : ' + str(self.settings['CAPTCHAR_RETRY_TIMES']))
        filename = 'quotes-' + response.url.split("/")[-2] + '.html'

        with open(filename, 'wb') as f:
            f.write(response.body)

