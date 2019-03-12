#!/bin/bash

# RESTful API 서버 실행 전,
# 크롤링 & elasticsearch에 인덱싱 작업을 진행 후, 이상 유무에 따라 서버를 실행한다.


# 테스트용 데이터 생성 및 인덱싱

# 크롤링으로 데이터 생성
echo "1. Generating csv files by crawling pages..." &&
python main.py test 1 &&

# Elasticsearch로 핑 테스트 후 docker 진행
echo "2. Indexing products information from csv files..." &&
python main.py test 2 &&

echo "3. Indexing query statistic file(.json) to index(/samples)..." &&
python main.py test 4
