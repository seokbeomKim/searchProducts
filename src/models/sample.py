#!/usr/bin/env python
# coding=utf-8

from elasticsearch_dsl import Document, Date, Integer, Double, \
                              Keyword, Text, Search, Nested, InnerDoc
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch

connections.create_connection(hosts=['localhost'])

class SampleCategory(InnerDoc):
  category = Keyword()
  statistic = Double()

class Sample(Document):
  class Index:
    name = 'samples'
    
  keyword = Text(analyzer='nori')
  categories = Nested(SampleCategory)
  
  @staticmethod
  def search(keyword = None):
    client = Elasticsearch()
    s = Search(using=client, index="samples")
    
    if keyword != None:
      s = s.filter('terms', keyword=[keyword])
      
    res = s.execute()
    return res
