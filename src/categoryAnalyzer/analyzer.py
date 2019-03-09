# coding=utf-8

import pickle
import re
import time
import os 
import numpy as np
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences

from .tokenizer import SimpleTokenizer

""" 상품명을 분석하여 카테고리를 반환하는 분석 개체
"""
class CategoryAnalyzer:

  def __init__(self, *args, **kwargs):
    print("CategoryAnalyzer instance has been initialized.")
    
    idx_cate_file = os.path.join(os.path.dirname(__file__), "example_idx_cate.pkl")
    model_file = os.path.join(os.path.dirname(__file__), "example_model.h5")
    
    self.idx_cate_dict = pickle.load(open(idx_cate_file, 'rb'))    
    self.model = load_model(model_file)
    self.tokenizer = SimpleTokenizer()    
    
  # Output으로 인한 시간 소모 줄이기 위해 출력 주석처리
  def getCategoryByName(self, name):
    start_time = time.time()
    # 모델의 예측은 각 카테고리별 확률값의 형태로 나오는데, 그 중 가장 확률이 높은 카테고리를 선택
    predict_result = self.model.predict(self.tokenizer.tokenize(name=name))[0]
    elapsed = time.time() - start_time

    # 확률이 가장 높은 카테고리를 미리 로드한 dict를 이용해 실제 상품 카테고리 이름으로 변경
    # 예측에 소요되는 시간은 0.1초 미만입니다.
    # print('{text}: \n\t{cate} in {sec} seconds\n'.format(text=name, cate=self.idx_cate_dict[np.argmax(predict_result)],
    #                                                     sec=elapsed))

    # 다음 코드는 분류 확률을 기준으로, 상위 N개의 분류 결과와 그 확률값을 구하는 방법입니다.
    # 4 번 문제(Elasticsearch Ranking Script)를 다른 방법으로 풀고자 할 때 참고하시면 됩니다.

    # 상위 몇 개의 분류 결과를 가져 올 것인지에 대한 변수
    topn = 3
    # 확률값을 기준으로 정렬하고, 정렬된 값의 index를 반환 후, 그 중 상위 N 개를 가져옴
    topn_indices = np.argsort(predict_result)[-topn:]
    # 상위 N 개의 확률값도 가져옴
    topn_scores = predict_result[topn_indices]

    # index를 실제 카테고리명으로 변경, 결과 확인
    # for i, s in zip(topn_indices, topn_scores):
    #     print('{cate}: {score}'.format(cate=self.idx_cate_dict[i], score=s))
        
    return self.idx_cate_dict[np.argmax(predict_result)]


  