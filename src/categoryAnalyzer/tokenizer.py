# coding=utf-8

"""상품명을 이용해 카테고리 분류를 진행하는 예시 코드

상품명을 이용한 카테고리 분류는 다음과 같은 방식으로 진행됩니다.

    1. 분류하고자 하는 상품명을 정제하고, 띄어쓰기를 진행
    2. 띄어쓰기 된 각 단어를 미리 생성한 단어 사전을 이용해 숫자로 변경
    3. 일정 길이의 단어로 자르기(혹은 padding을 이용한 dummy 정보 채우기)
    4. 모델에 결과 예측
    5. 모델에서 예측된 결과(숫자)를 실제 카테고리 명으로 변경

이 과정들에 대한 예시 코드입니다.

예시 코드를 활용하여 문제 풀이를 진행해 주세요.
이 코드 부분에 대한 문의는 엘튼(elton@buzzni.com)으로 문의해 주시면 됩니다.

"""

import pickle
import re
import time
import os

import numpy as np
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences


class SimpleTokenizer(object):
    """ 상품명을 이용해 카테고리 분류를 수행할 때 필요한 토크나이저(띄어쓰기를 해 주는 도구)에 대한 정의

        __init__ 메소드에서는 띄어쓰기 과정에서 사용될 상수들을 저장하고, 기존에 미리 저장된 객체를 로드합니다.
        filter_name 메소드에서는 상품명을 정제합니다.
        tokenize 메소드에서는 상품명을 모델에서 사용하는 형태로 변경해줍니다.

        Args:
            max_seq_len (int): 상품별 최대 단어 갯수에 대한 값입니다. 입력을 받을 수 있도록 하였지만, 변경 시 모델에서 예측이 불가능해집니다.
    """

    def __init__(self, max_seq_len=25):
        """ SimpleTokenizer 클래스의 __init__ 메소드

        Args:
            max_seq_len (int): 상품별 최대 단어 갯수에 대한 값
        """
        # 상품명에서 제거 될 불필요한 키워드들 - 변경 시 모델 성능에 영향을 미칠 수 있음
        self.stop_words = '롯데백화점,무료배송,정품,현대백화점,하프클럽,추천,개,핫트랙스,바보사랑,아트박스,빠른배송,중고,대,국산,사은품,텐바이텐' \
                          ',할인,방문,가격,인하,개월,할인,매,당일발송,갤러리아'.split(',')

        # 유효 단어로 인정 할 단어당 최소 음절 갯수 - 변경 시 모델 성능에 영향을 미칠 수 있음
        self.min_word_len = 2

        # 단어별 index와, 단어 사전에 존재하지 않은 단어를 발견했을 때를 처리하기 위하여, 미리 저장된 객체 로드
        tokenizer_file = os.path.join(
            os.path.dirname(__file__), "example_tokenizer.pkl")
        self.tokenizer = pickle.load(open(tokenizer_file, 'rb'))

        # 상품별 최대 단어 갯수 - 변경시 모델에서 예측이 불가능
        self.max_seq_len = max_seq_len

    def filter_name(self, name):
        """ 상품명에서 불필요한 키워드를 제거하는 메소드

        상품명에서 불필요한 키워드들을 제거합니다.
        특수문자를 제거하고, self.stop_words에 해당하는 단어를 제거하며, self.min_word_len 보다 작은 단어를 제거합니다.

        tokenize 메소드에서 사용됩니다.

        Args:
            name (str): 상품명

        Returns:
            정제된 상품명
        """
        return u' '.join(filter(lambda e: len(e) >= self.min_word_len and e not in self.stop_words,
                                map(lambda i: i.strip(),
                                    re.sub('[!@#$~*+=_:;,.×\(\)\'\[\]\-\/\d]', ' ', name).split(' '))))

    def tokenize(self, name):
        """ 상품명을 모델의 입력 형태에 맞게 바꿔주는 함수

        분류 모델을 통해 상품의 카테고리를 예측하기 위해서 미리 정의된 모델의 입력의 형식에 맞춰 주어야 합니다.
        다음과 같은 과정을 통해 진행됩니다.

        1. filter_name 메소드를 이용한 상품명 정제
        2. 미리 저장된 tokenizer 객체를 이용하여 단어를 숫자로 바꾸기
        3. self.max_seq_len 에 지정된 길이에 맞추어 전체 길이를 조절하기 (상품명이 짧다면 padding, 길다면 잘라내기)
        4. 리스트로 바꾸어 리턴

        Args:
            name (str): 모델의 입력으로 바꾸고자 하는 상품명

        Returns:
            모델의 입력 형태로 변환된 list
        """

        # 상품명 정제
        filtered = self.filter_name(name=name)

        # 단어 -> 숫자 변환
        seq = self.tokenizer.texts_to_sequences([filtered])

        # 길이 조절
        return [pad_sequences(seq, maxlen=self.max_seq_len)]
