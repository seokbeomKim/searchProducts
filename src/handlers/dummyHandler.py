# -*- coding: utf-8 -*-
import abc
from .handlerInterface import *


class DummyHandler(IHandler):
    """더미용 Request Handler
    """

    def handle(self, data):
        return "DUMMY DATA"
