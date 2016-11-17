import random, math, subprocess, re

import scrapy
from scrapy.http import Request
from ..items import *


class ZhixingSpider(scrapy.Spider):
    '''爬取 http://zhixing.court.gov.cn/search/ 的数据 '''
    name = 'Zhixing'
    identcodea = 0
    domain = "http://zhixing.court.gov.cn/"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"
    }

    start_urls = [
        "http://zhixing.court.gov.cn/search/"
    ]

    def start_requests(self):
        yield Request("http://zhixing.court.gov.cn/search/",
                      meta={'cookiejar': 1, 'dont_obey_robotstxt': True}, headers=self.headers, callback=self.parse_homepage)

    def parse_homepage(self, response):
        return [self.get_captcha_request(response.meta, type='newsearch')]

    # def parse_list(self, response):
    #
    #
    # # 解析返回的查询列表


    def parse_captcha(self, response):
        # 处理验证码图片
        identCode = None
        captcha_file_name = 'captcha.jpg'
        with open(captcha_file_name, 'wb') as fp:
            fp.write(response.body)

        strRec = subprocess.getoutput('tesseract ./captcha.jpg stdout -l eng 2>/dev/null')
        strNums = re.findall(r'\d+', strRec)
        strTmp = ''
        for strNum in strNums:
            strTmp += strNum

        if strTmp is not '':
            identCode = int(strTmp)
            print("identcode is : " + str(identCode))

        if response.meta['type'] == 'newsearch':
            listUrl = self.domain + 'search/newsearch'
            self.identcodea = identCode
            yield scrapy.FormRequest(
                    url=listUrl,
                    headers=self.headers,
                    formdata={
                        'currentPage': "1",
                        'searchCourtName': "全国法院（包含地方各级法院）",
                        'selectCourtId': "1",
                        'selectCourtArrange': "1",
                        'pname': '梁忠文',
                        'cardNum': "",
                        'j_captcha': str(identCode)
                    },
                    meta=response.meta,
                    callback=self.parse_list
            )

        elif response.meta['type'] == 'newdetail':
            detailUrl = self.domain + 'search/newdetail?id=' + response.meta['id'] + '&j_captcha=' + str(identCode)
            yield scrapy.Request(
                    url=detailUrl,
                    headers=self.headers,
                    meta=response.meta,
                    callback=self.parse_detail
            )

    def parse_list(self, response):
        # 获取被执行list 并解析
        # 检查是否验证码输入错误
        filename = 'zhixing.html'
        with open(filename, 'wb') as fp:
            fp.write(response.body)

        if re.search(r'验证码出现错误', response.body.decode('utf-8')):
            self.logger.info('验证码出现错误, 重试----')
            yield self.get_captcha_request(response.meta, retry=1)
            return []

        detailIds = response.xpath('//a/@id').extract()
        for detailId in detailIds:
            yield self.get_captcha_request(response.meta, type='newdetail', id=detailId, cookiejar=int(detailId))

        # detailId = detailIds[0]
        # yield self.get_captcha_request({}, type='newdetail', id=detailId, cookiejar=int(detailId))
        #
        # nexts = response.xpath('//a[text()="下一页"]/@onclick').re(r'gotoPage\((\d+)\)')

        # listUrl = self.domain + 'search/newsearch'
        # yield scrapy.FormRequest(
        #             url=listUrl,
        #             headers=self.headers,
        #             formdata={
        #                 'currentPage': "3",
        #                 'searchCourtName': "全国法院（包含地方各级法院）",
        #                 'selectCourtId': "1",
        #                 'selectCourtArrange': "1",
        #                 'pname': '杨乃义',
        #                 'cardNum': "",
        #                 'j_captcha': str(self.identcodea)
        #             },
        #             meta=response.meta,
        #             callback=self.parse_list
        #     )
        #
        # return []
        # for next in nexts:

    # totalPage = 0;
    # ret = re.findall(r'var\s+totalPage\s*=\s*(\d+);', response.body)
    # if len(ret) > 0:
    #     totalPage = int(ret[0])
    #
    # for pageIndex in range(2, totalPage + 1):
    #     yield


    def parse_detail(self, response):
        # 解析获取到的详细信息
        if response.body_as_unicode() == '{}':
            return [self.get_captcha_request(response.meta, retry=1)]

        print(response.body_as_unicode())
        return None

    def get_captcha_request(self, prev_meta, **args):
        imageUrl = 'http://zhixing.court.gov.cn/search/security/jcaptcha.jpg?' + str(math.floor(random.random() * 100))
        # print(imageUrl)
        metaData = prev_meta
        metaData.update(args)

        if 'retry' in metaData and metaData['retry'] == 1:
            metaData['retryTimes'] = \
                (metaData['retryTimes'] - 1 if 'retryTimes' in metaData else self.settings['CAPTCHAR_RETRY_TIMES'])

            self.logger.info('重新获取验证码,剩余次数: %d', metaData['retryTimes'])
            if metaData['retryTimes'] <= 0:
                self.logger.info('重试结束仍然不能获取到验证码')
                return []

        # print(metaData)

        return scrapy.Request(
                url=imageUrl,
                headers=self.headers,
                meta=metaData,
                callback=self.parse_captcha,
                dont_filter=True
        )
