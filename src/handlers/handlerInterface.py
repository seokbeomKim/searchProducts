# -*- coding: utf-8 -*-

from abc import ABC, ABCMeta, abstractmethod


class IHandler(ABC):

    __metaclass__ = ABCMeta

    @abstractmethod
    def handle(self, data):
        raise NotImplemented
