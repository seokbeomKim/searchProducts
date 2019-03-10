# -*- coding: utf-8 -*-
from tests import Tester

"""테스트 케이스 실행하기 위한 설정 플래그. 테스트 케이스 외의 코드는 실행하지 않는다.
TC1: Crawling
TC2: Category analyzing
TC3: Sending a query to Elasticsearch 
"""
isTesting = True

if __name__ == '__main__':
  
  if (isTesting):
    """
    테스팅 플래그가 활성화되어 있는 경우, 정상적인 API 서버 실행 대신에, 
    지정한 테스트 케이스를 실행한다.
    """
    print ("Running in testing mode...")
    
    print ("> 1. Crawling test: Hsmoabot")
    tcRunner = Tester()
    # tcRunner.testcase1()
    
    print ("> 2. Categorizing test: using tensorflow, get a category & index to elatricsearch...")
    # tcRunner.testcase2()
    
    print ("> 3. Testing search...")
    # tcRunner.testcase3()
    
    print ("> 4. Import json file to elasticsearch")
    # tcRunner.testcase4()
    # tcRunner.testCategorize()
    # tcRunner.testSearching()
    
    print ("> 5. Getting items with score adjustment")
    tcRunner.testcase5()
