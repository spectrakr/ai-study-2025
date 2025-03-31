## Elasticsearch에 BM25를 사용하는 방법

- 사전에 인덱스를 만들어 놓지 않으면 analyzer가 적용이 되지 않는다.
- 한국어에 대해서는 nori analyzer를 사용해야 한다.
- 불용어 제거를 위해 nori_filter를 적용한다.
- 그래서 아래 스크립트로 인덱스를 미리 만들어 놓고 사용하는 것이 좋다.
- 인덱스 만들 때 아래 인덱스명(kmhan_pdf)은 본인이 사용하는 이름으로 변경해야 한다.


```http
PUT kmhan_pdf
{
  "settings": {
    "analysis": {
      "tokenizer": {
        "custom_nori_tokenizer": {
          "type": "nori_tokenizer"
        }
      },
      "analyzer": {
        "custom_nori_analyzer" : {
          "tokenizer" : "custom_nori_tokenizer",
          "filter": [              
            "nori_filter",
            "lowercase"
          ]
        }
      },
      "filter": {          
       "nori_filter": {
         "type": "nori_part_of_speech",            
         "stoptags": []
       }
      }
    }
  },
  "mappings": {
    "properties": {
      "value": {
        "type": "keyword"
      },
      "timestamp": {
        "type": "date"
      },
      "text" : {
        "type" : "text",
        "analyzer" : "custom_nori_analyzer",
        "fields" : {
          "keyword" : {
            "type" : "keyword",
            "ignore_above" : 256
          }
        }
      }
    }
  }
}
```
