import sys
import os
import csv
import pandas
import datetime
from elasticsearch import Elasticsearch

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
    
  def testSearching(self):
    """Elasticsearch 내에서 검색 키워드 테스트
    """
    product = Products.search()
    print(product)
