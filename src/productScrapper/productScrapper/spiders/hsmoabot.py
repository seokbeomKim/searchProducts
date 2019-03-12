# -*- coding: utf-8 -*-

import scrapy
import datetime
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy import signals


class HsmoabotSpider(scrapy.Spider):
    """
    Hsmoa 페이지 크롤링 봇 클래스
    """
    name = 'hsmoabot'
    allowed_domains = ['hsmoa.com']
    start_urls = ['http://hsmoa.com/?date=']

    def __init__(self, name=None, target_date=None, **kwargs):
        super().__init__(name=name, **kwargs)
        if target_date != None:
            self.start_urls = ['http://hsmoa.com/?date=' + target_date]

    @staticmethod
    def crawlingMonth(end_year, end_month, end_day):
        """ 인자로 전달받은 날짜에서 한달(30일)치 데이터를 가져온다.
        :type end_year: Integer
        :param end_year: 크롤링 마지막 날의 연도

        :type end_month: Integer
        :param end_month: 크롤링 마지막 날의 월

        :type end_day: Integer
        :param end_day: 크롤링 마지막 날의 일

        :raises: None

        :rtype: None
        """
        runner = CrawlerRunner({
            'USER_AGENT': 'MOZILLA/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'FEED_FORMAT': 'csv',
            'LOG_ENABLED': 'False'
        })

        end_date = datetime.date(end_year, end_month, end_day)
        for i in range(0, 30):
            dateStr = end_date.strftime("%Y%m%d")
            runner.settings['FEED_URI'] = "./generated/" + dateStr + ".csv"
            runner.settings['TARGET_DATE'] = dateStr
            runner.crawl(HsmoabotSpider, target_date=dateStr)

            end_date = end_date - datetime.timedelta(1)

        d = runner.join()
        d.addBoth(lambda _: reactor.stop())

        reactor.run()

    def parse(self, response):
        productName = response.css('.disblock') \
            .xpath('div[@class="display-table"]/div[3]') \
            .css('.font-15,.font-13') \
            .xpath('text()') \
            .re(r"\s*(.*.)\s*")
        seller = response.xpath('//div[@class="display-table"]/div[3]/img') \
            .xpath('@src') \
            .re(r"^.*/logo/logo_(.*.)\.png")
        price = response.css('.disblock') \
            .xpath('div[2]/div[3]/s').xpath('text()') \
            .re(r"(^.*)+원")
        price = [s.replace(',', '') for s in price]
        # 메인으로 돌아가는 버튼 제외하기 위해 url 부분에도 정규식 추가
        url = response.css('.disblock').xpath('@href').re(r"^/i?.*.$")

        for item in zip(productName, seller, price, url):
            scraped_info = {
                'productName': item[0].strip(),
                'seller': item[1].strip(),
                'price': item[2].strip(),
                'url': item[3].strip(),
            }
            yield scraped_info
