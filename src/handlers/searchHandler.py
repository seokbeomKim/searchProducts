# -*- coding: utf-8 -*-

from helpers import *
from models import *
from productScrapper import *
from categoryAnalyzer import *
from elasticsearch import Elasticsearch
from elasticsearch_dsl import query, function
from .handlerInterface import IHandler
import sys
import os
import csv
import pandas
import datetime
import abc

sys.path.append(os.path.join(os.path.dirname(__file__), "../categoryAnalyzer"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../productScrapper"))


class SearchHandler(IHandler):
    """GET /search?keyword={키워드}
    사용자가 전달한 키워드 중심으로 검색한 결과를 반환한다. 
    이 때, 전달하는 데이터로 'keyword'는 필수로 전달해야 한다.

    [SEARCH 검색 GET 파라미터]
    - keyword: 검색 메인 키워드
        /search?keyword=의류
    - priceRange: 검색 가격 대 [Gte, Lt)
        /search?keyword=의류&priceRange=1000,5000
    - category: 상품 카테고리
        /search?keyword=바지&category=의류
    - resultFrom: 검색 결과 인덱스 설정 
      (검색한 결과값들로 페이지 구성을 할 수 있도록 시작 인덱스를 설정)
        /search?keyword=&resultFrom=100 
    - resultSize: 검색 결과 크기
        /search?keyword=&resultSize=100
    """

    def handle(self, args):

        if not args:
            return ""

        keyword = args.get('keyword')
        priceRange = args.get('priceRange')
        category = args.get('category')
        resultFrom = args.get('from')
        resultSize = args.get('size')

        # 검색을 위한 검색 키워드는 반드시 있어야 한다.
        if keyword == None:
            keyword = ''

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

        # elasticsearch 쿼리 베이스
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
        if args.get('resultFrom'):
            """검색 결과 인덱스 시작점을 설정
            """
            d['from'] = args.get('resultFrom')

        if args.get('resultSize'):
            d['size'] = args.get('resultSize')

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

        return Products.searchQuery(d)
