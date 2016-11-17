# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class QuoteItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    text = scrapy.Field
    author = scrapy.Field()
    pass


class ZhixingItem(scrapy.Item):
    name = scrapy.Field(serializer=str)
    idCode = scrapy.Field()
    courtName = scrapy.Field()
    disruptTime = scrapy.Field()
    caseCode = scrapy.Field()
    product = scrapy.Field()
