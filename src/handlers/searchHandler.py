# -*- coding: utf-8 -*-

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

from categoryAnalyzer import *
from productScrapper import *
from models import *
from helpers import *
from errors import *

class SearchHandler(IHandler):
  """/search
  키워드에 해당하는 상품을 검색한 뒤 
  """
  def handle(self, keyword):
    
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
      innerSource += 'if (doc["category"].value == "' + c + '") { return (_score + ' + str(score) + '); }'
      
    d = {
      'function_score': {
        'query': {
          'match_phrase': {
            'productName': keyword
          }
        },
        'script_score': {
          'script': {
            'lang': 'painless',
            'source': innerSource
          }
        }
      }
    }
    
    q = query.Q(d)
    return Products.searchWithQueue(q)
