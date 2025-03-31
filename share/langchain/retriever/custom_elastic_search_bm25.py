from typing import Dict, List
from langchain_community.retrievers import ElasticSearchBM25Retriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document

from apps.slack.elastic.slack_message_elastic_client import slack_issue_docs_name
from rag.vector_stores.elasticsearch import sis_ticket_docs_name
from share.elastic_client import elasticsearch_client
from share.share_lib import ShareLib


class CustomSisElasticSearchBM25Retriever(ElasticSearchBM25Retriever):
    filter: Dict = {}
    k = 4
    keywords = []

    def build_filter_query(self) -> List:
        _filter_query = []
        _filter = self.filter.get("filter")

        if _filter:
            for key, value in _filter.items():
                _filter_query.append({"term": {f"metadata.{key}.keyword": f"{value}"}})

        return _filter_query

    def append_keyword_query(self, must_clauses: List) -> List:
        for keyword in self.keywords:
            must_clauses.append({"match_phrase": {"text": keyword}})
        return must_clauses

    def _get_relevant_documents(
        self, query: str, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        must_clauses = self.build_filter_query()
        must_clauses = self.append_keyword_query(must_clauses=must_clauses)
        must_clauses.append(({"match": {"text": query}}))
        query_dict = {"query": {"bool": {"must": must_clauses}}, "size": self.k}
        res = self.client.search(index=self.index_name, body=query_dict)
        docs = []
        for r in res["hits"]["hits"]:
            docs.append(
                Document(
                    page_content=r["_source"]["text"], metadata=r["_source"]["metadata"]
                )
            )
        return docs


if __name__ == "__main__":
    question = "프론트 API"
    # channel_key = "C061EKM9UQ2"
    search_kwargs = {"filter": {}}
    # search_kwargs["filter"]["channel_id"] = channel_key
    custom_bm25_retrievel = CustomSisElasticSearchBM25Retriever(
        client=elasticsearch_client,
        index_name=sis_ticket_docs_name,
        filter=search_kwargs,
        # keywords=["우리은행", "SSO"],
        k=2,
    )
    ShareLib.print_docs_pretty(custom_bm25_retrievel.invoke(question))
