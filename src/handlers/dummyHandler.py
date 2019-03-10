# -*- coding: utf-8 -*-
import abc
from .handlerInterface import *

class DummyHandler(IHandler):
  """더미용 Request Handler
  추후, 클라이언트 측에서 RESTful API 테스팅을 위해 사용
  """
  def handle(self, data):
    return "DUMMY DATA"
