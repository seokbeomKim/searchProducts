# -*- coding: utf-8 -*-

import json


class JsonRBuilder(object):
    """Json Return value Builder
    RESTful API 결과값으로서 *.json 형태로 출력하기 위한 Builder 클래스
    """

    @staticmethod
    def build(request_path=None, data=None):
        return json.dumps({
            'path': request_path,
            'data': data
        })
