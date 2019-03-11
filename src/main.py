# -*- coding: utf-8 -*-
import json
import sys

from flask import Flask, request, Response
from tests import Tester
from helpers import JsonRBuilder
from handlers import SearchHandler, DummyHandler

isTesting = True

if __name__ == '__main__':

    if (isTesting):
        """
        테스팅 플래그가 활성화되어 있는 경우, 정상적인 API 서버 실행 대신에, 
        지정한 테스트 케이스를 실행한다.
        """
        print("Running in testing mode...")

        tcRunner = Tester()
        tcRunner.runTestcases(sys.argv)

        # 테스트 케이스 실행이 끝나면 스크립트를 종료
        exit(0)

app = Flask('SimpleSearchEngine')
handlers = {
    "/": DummyHandler(),
    "/dummy": DummyHandler(),
    "/search": SearchHandler()
}


@app.route('/')
@app.route('/dummy', methods=['GET'])
@app.route('/search', methods=['GET'])
def searchKeyword():
    if request.method == 'GET':

        if len(request.args) > 0:
            res = handlers[request.path].handle(request.args)
        else:
            res = "Keyword is empty"

    resJson = JsonRBuilder.build(request_path=request.path, data=res)

    return Response(resJson, content_type='application/json; charset=utf-8')
