import sys
import os
import csv
import pandas
import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import query, function

sys.path.append(os.path.join(os.path.dirname(__file__), "../categoryAnalyzer"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../productScrapper"))

from categoryAnalyzer import *
from productScrapper import *
from models import *
from helpers import *

class Tester(object):
  
  def testcase1(self):
    """한 달 가량의 데이터를 크롤링하여 결과 파일이 정상적으로 생성되는지 확인한다.    
    """
    HsmoabotSpider.crawlingMonth(2019, 3, 1)
    
  def testcase2(self):
    """크롤링한 데이터 중심으로 elasticsearch에 인덱싱하는 테스트 케이스
    """
    dataIndexer = DataIndexer()
    csvDir = os.path.join(os.path.dirname(__file__), "..")
    csvFiles = os.listdir(csvDir)
    csvFiles = [fname for fname in csvFiles if fname.endswith('.csv')]
    
    for f in csvFiles:
      print("Read a file: " + f)
      dataIndexer.readAndIndexFile(os.path.join(csvDir, f))
  
  def testcase3(self):
    """elasticsearch 내에서 검색하는 테스트
    """
    tc1 = Products.search(productName="압력")
    tc2 = Products.search(seller="lottemall")
    tc3 = Products.search(category="출산/육아")
    tc4 = Products.search(price_range = (50000, 100000))
    tc5 = Products.search(productName="보험", price_range = (150000, 500000))
    
  def testcase4(self):
    """예제파일(*.json, 통계자료) import 예제
    """ 
    jsonPath = os.path.join(os.path.dirname(__file__), "../example.json")
    importer = StatisticImporter()
    importer.importJson(jsonPath)
    
  def testcase5(self):
    """키워드로 검색한 물품에 대해, 가중치 조정한 쿼리 결과 얻는 테스트
    """
    tcKeyword = '바지'
    
    # 후보자로 등록할 통계 오차 한계
    tcThreshold = 0.2
    
    # Step 1. 
    # 쿼리 통계 자료로부터 유력한 카테고리 정보를 얻는다.
    samples = Sample.search(keyword=tcKeyword)
    
    categoryCandidates = []
    weighCandidates = []
    for s in samples:
      previous_score = s.categories[0].statistic
        
      for category in s.categories:
        if abs(category.statistic - previous_score) < tcThreshold:
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
            'productName': tcKeyword
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
    Products.searchWithQueue(q)
  
  def testSearching(self):
    """Elasticsearch 내에서 검색 키워드 테스트
    """
    product = Products.search()
    print(product)
