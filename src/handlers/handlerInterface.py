# -*- coding: utf-8 -*-

from abc import ABC, ABCMeta, abstractmethod


class IHandler(ABC):

    """ RESTful API Request 핸들러 인터페이스 """

    __metaclass__ = ABCMeta

    @abstractmethod
    def handle(self, data):
        raise NotImplemented
