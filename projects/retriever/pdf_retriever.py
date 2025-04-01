from langchain.retrievers import EnsembleRetriever

from projects.store.pdf_store import PdfStore
from share.langchain.retriever.custom_elastic_search_bm25 import (
    CustomElasticSearchBM25Retriever,
)


class PdfRetriever(object):

    @classmethod
    def get_bm25_retriever(cls, index_name):
        return CustomElasticSearchBM25Retriever(
            client=PdfStore.elasticsearch_client, index_name=index_name, k=3
        )

    @classmethod
    def ger_ensemble_retriever(cls, index_name: str, vector_retriever):
        return EnsembleRetriever(
            retrievers=[
                cls.get_bm25_retriever(index_name),
                vector_retriever,
            ],
            weights=[0.5, 0.5],
        )
