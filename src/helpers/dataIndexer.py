# -*- coding: utf-8 -*-

from models import *
from productScrapper import *
from categoryAnalyzer import *
import os
import sys
import csv
import pandas
from elasticsearch import Elasticsearch

sys.path.append(os.path.join(os.path.dirname(__file__), "../categoryAnalyzer"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../productScrapper"))


class DataIndexer(object):
    """크롤링한 데이터를 파싱하여 elasticsearch 검색엔진으로 인덱싱하는 객체
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analyzer = CategoryAnalyzer()

    def readAndIndexFile(self, filepath):
        """ 크롤링하여 생성한 파일을 읽어들여 ElasticSearch에 인덱싱한다.
        :type filepath: string
        :param filepath: csv 파일 절대 경로
        :rtype: 인덱싱 결과
        """
        df = pandas.read_csv(filepath)

        for index, row in df.iterrows():
            category = self.analyzer.getCategoryByName(row['productName'])
            row['category'] = category
            self.indexRowData(row)

        return row

    def indexRowData(self, data):
        product = Products(productName=data['productName'],
                           seller=data['seller'],
                           price=data['price'],
                           url=data['url'],
                           category=data['category'])
        product.save()
