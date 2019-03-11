# -*- coding: utf-8 -*-

from models import *
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "../categoryAnalyzer"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../productScrapper"))


class StatisticImporter(object):
    """주어진 통계자료를 elasticsearch에 import하는 helper class
    이 때, 기존 json 파일 내 카테고리 배열 요소가 가지는 배열 형태를 
    스크립트에서 사용하기 쉽도록 "category"와 "statistic"으로 나누어 재구성한다.
    """

    def importJson(self, filepath):
        jsondata = open(filepath).read()
        data = json.loads(jsondata)

        for keyword in data:
            newSample = Sample()
            newSample.keyword = keyword

            for category in data[keyword]:
                newSample.categories.append({
                    "category": category[0],
                    "statistic": category[1]
                })

            newSample.save()
