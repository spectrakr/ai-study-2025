from typing import List

from elasticsearch import Elasticsearch
from langchain_community.retrievers import ElasticSearchBM25Retriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document


class CustomElasticSearchBM25Retriever(ElasticSearchBM25Retriever):
    def __init__(
        self, client: Elasticsearch, index_name: str, filter: dict = {}, k: int = 4
    ) -> None:
        super().__init__(client=client, index_name=index_name)
        self._k = k
        self._filter = filter

    def build_filter_query(self) -> List:
        _filter_query = []
        _filter = self._filter.get("filter")  # self._filter 사용

        if _filter:
            for key, value in _filter.items():
                _filter_query.append({"term": {f"metadata.{key}.keyword": f"{value}"}})

        return _filter_query

    def _get_relevant_documents(
        self, query: str, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        must_clauses = self.build_filter_query()
        must_clauses.append(({"match": {"text": query}}))
        query_dict = {
            "query": {"bool": {"must": must_clauses}},
            "size": self._k,
        }  # self._k 사용
        res = self.client.search(index=self.index_name, body=query_dict)
        docs = []
        for r in res["hits"]["hits"]:
            doc = Document.model_validate(
                {
                    "page_content": r["_source"]["text"],
                    "metadata": r["_source"]["metadata"],
                }
            )
            docs.append(doc)
        return docs


if __name__ == "__main__":
    question = "형태"
    search_kwargs = {"filter": {}}
    # search_kwargs["filter"]["channel_id"] = channel_key
    elasticsearch_client = Elasticsearch("http://172.16.120.203:9201")
    index_name = "kmhan_pdf"
    custom_bm25_retriever = CustomElasticSearchBM25Retriever(
        client=elasticsearch_client,
        index_name=index_name,
        filter=search_kwargs,
        k=2,
    )
    result = custom_bm25_retriever.invoke(question)
    print(result)
