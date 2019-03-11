# -*- coding: utf-8 -*-

from helpers import *
from models import *
from productScrapper import *
from categoryAnalyzer import *
import sys
import os
import csv
import pandas
import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import query, function
import abc
from .handlerInterface import IHandler

sys.path.append(os.path.join(os.path.dirname(__file__), "../categoryAnalyzer"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../productScrapper"))


class SearchHandler(IHandler):
    """/search
    사용자가 전달한 검색 방법으로 검색한 뒤 앞선 레코드 10개를 반환한다.
    """

    def handle(self, args):

        if not args:
            return ""

        keyword = args.get('keyword')
        priceRange = args.get('priceRange')
        category = args.get('category')

        # 검색을 위한 검색 키워드는 반드시 있어야 한다.
        if keyword == None:
            return ""

        # 후보자로 등록할 통계 오차 한계
        threshold = 0.2

        # Step 1.
        # 쿼리 통계 자료로부터 유력한 카테고리 정보를 얻는다.
        samples = Sample.search(keyword=keyword)

        categoryCandidates = []
        weighCandidates = []
        for s in samples:
            previous_score = s.categories[0].statistic

            for category in s.categories:
                if abs(category.statistic - previous_score) < threshold:
                    """
                    1순위와 2순위 후보 간의 차이가 얼마 되지 않는 경우(임의로 threshold 정함),
                    1순위와 2순위를 카테고리 후보에 등록한다.
                    쿼리 결과는 스코어가 높은 순서대로 적용되므로, 배열에는 스코어 순으로 
                    카테고리 후보자가 등록된다.
                    """
                    if not category.category in categoryCandidates:
                        categoryCandidates.append(category.category)
                        weighCandidates.append(category.statistic)
                        previous_score = category.statistic

        # Step 2.
        # 실제 상품 인덱스에 쿼리를 보내고, 후보자들 개수만큼 가중치를 두어
        # 스코어를 조정한다.
        innerSource = ""

        # painless 관련 코드 추가 부분
        for idx, c in enumerate(categoryCandidates):
            score = weighCandidates[idx] / (idx + 1)
            if idx != 0:
                innerSource += 'else '
            innerSource += 'if (doc["category"].value == "' + \
                c + '") { return (_score + ' + str(score) + '); }'

        d = {
            'query': {
                'function_score': {
                    'query': {
                        'bool': {
                            'must': [
                                # {'match_phrase': {'productName': keyword}},
                                # {'match': {'category': category}},
                                # {'range': {'price': {'gte': gte, 'lt': lt}}}
                            ]
                        }
                    }
                }
            }
        }

        if innerSource:
            d['query']['function_score']['script_score'] = {
                'script': {
                    'lang': 'painless',
                    'source': innerSource
                }}

        # 쿼리 조정
        if args.get('keyword'):
            d['query']['function_score']['query']['bool']['must'].append(
                {'match_phrase': {
                    'productName': args.get('keyword')
                }})
        if args.get('category'):
            d['query']['function_score']['query']['bool']['must'].append(
                {'match': {
                    'category': args.get('category')
                }})
        if args.get('priceRange'):
            priceRange = args.get('priceRange').split(',')
            d['query']['function_score']['query']['bool']['must'].append(
                {'range': {
                    'price': {
                        'gte': priceRange[0],
                        'lt': priceRange[1]
                    }
                }})

        # q = query.Q(d)
        return Products.searchQuery(d)
