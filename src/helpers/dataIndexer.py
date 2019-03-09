# -*- coding: utf-8 -*-

import os
import sys
import csv
import pandas
from elasticsearch import Elasticsearch

sys.path.append(os.path.join(os.path.dirname(__file__), "../categoryAnalyzer"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../productScrapper"))

from categoryAnalyzer import *
from productScrapper import *
from models import *

class DataIndexer(object):
  """크롤링한 데이터를 파싱하여 elasticsearch 검색엔진으로 인덱싱하는 객체
  """
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.analyzer = CategoryAnalyzer()
  
  def readAndIndexFile(self, filepath):
    df = pandas.read_csv(filepath)
    
    for index, row in df.iterrows():
      category = self.analyzer.getCategoryByName(row['productName'])
      row['category'] = category
      self.indexRowData(row)
      
    return row

  def indexRowData(self, data):
    product = Products(productName=data['productName'], \
                        seller=data['seller'], \
                        price=data['price'], \
                        url=data['url'], \
                        category=data['category'])
    product.save()
