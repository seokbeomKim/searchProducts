#!/bin/bash

# curl 이용하여 products, samples 두 인덱스에 대한 맵핑 사전 설정

# samples: 통계 예시자료
curl -X PUT -d '
{
  "mappings" : {
    "doc" : {
      "properties" : {
        "categories" : {
          "type" : "nested",
          "properties" : {
            "category" : {
              "type" : "text"
            },
            "statistic" : {
              "type" : "float"
            }
          }
        },
        "keyword" : {
          "type" : "text",
          "analyzer" : "nori"
        }
      }
    }
  }
}
' $SSE_HOST:9200/samples -H 'content-type: application/json'

# products: 크롤링 데이터용 인덱스
curl -X PUT -d '
{
  "mappings" : {
    "doc" : {
      "properties" : {
        "category" : {
          "type" : "keyword"
        },
        "price" : {
          "type" : "integer"
        },
        "productName" : {
          "type" : "text",
          "analyzer" : "nori"
        },
        "seller" : {
          "type" : "keyword"
        },
        "url" : {
          "type" : "text"
        }
      }
    }
  }
}' $SSE_HOST:9200/products -H 'content-type: application/json'
