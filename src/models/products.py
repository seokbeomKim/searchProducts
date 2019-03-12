#!/usr/bin/env python
# coding=utf-8

from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, Search
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch
import os


class Products(Document):

    # Inner class
    class Index:
        name = 'products'

    productName = Text(analyzer='nori')   # 상품명
    seller = Keyword()       # 쇼핑사명
    price = Integer()         # 상품가
    url = Text()         # 관련 URL
    category = Keyword()

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def save(self, **kwargs):
        return super(Products, self).save(** kwargs)

    @staticmethod
    def search(productName=None, seller=None, category=None, price_range=None):
        client = Elasticsearch(os.environ['SSE_HOST'])
        s = Search(using=client, index="products")

        if productName != None:
            """
            상품명의 경우 형태소 분석기 nori를 이용하여 term 단위로 구분할 수 있다.
            """
            s = s.filter('terms', productName=[productName])

        if seller != None:
            s = s.filter('match', seller=seller)

        if category != None:
            s = s.filter('match', category=category)

        if price_range != None:
            """
            가격 범위는 튜플 형태로 받는다 [GTE, LT)
            """
            s = s.filter('range', price={
                         "gte": price_range[0], "lt": price_range[1]})

        res = s.execute()

        return res

    @staticmethod
    def searchQuery(data=None):
        if data != None:
            es = Elasticsearch(os.environ['SSE_HOST'])
            res = es.search(
                index="products",
                body=data
            )

            rvalue = []
            for r in res['hits']['hits']:
                rv = r['_source']
                rvalue.append({
                    'productName': rv['productName'],
                    'price': rv['price'],
                    'seller': rv['seller'],
                    'url': rv['url'],
                    'category': rv['category']
                })

            return rvalue
