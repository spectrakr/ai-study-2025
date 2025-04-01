import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from share.slack.util.logger import setup_logger

load_dotenv()

logger = setup_logger(__name__)


class ElasticClient:
    elasticsearch_url = os.getenv("ELASTICSEARCH_HOST")
    logger.info(f"init elastic client host : {elasticsearch_url}")
    elasticsearch_client = Elasticsearch(elasticsearch_url)

    @classmethod
    def get_all_docs(cls, index):
        response = cls.elasticsearch_client.search(
            index=index, query={"match_all": {}}, size=1000
        )

        return [hit["_source"] for hit in response["hits"]["hits"]]

    @classmethod
    def get(cls, index_name: str, doc_id: str):
        """ID 기반 문서 조회"""
        response = cls.elasticsearch_client.get(
            index=index_name, id=doc_id, ignore=[404]
        )
        if response and response.get("found"):
            return response["_source"]
        return None

    @classmethod
    def upsert_doc(cls, index, _id, doc):
        logger.info(f"upsert index = {index} , doc = {doc}")
        cls.elasticsearch_client.update(
            index=index, id=_id, doc=doc, doc_as_upsert=True
        )

    @classmethod
    def delete_doc(cls, index, _id):
        cls.elasticsearch_client.delete(
            index=index,
            id=_id,
        )

    @classmethod
    def create_index(cls, index_name, settings=None):
        if not cls.elasticsearch_client.indices.exists(index=index_name):
            cls.elasticsearch_client.indices.create(index=index_name, body=settings)
            logger.info(f"Project index '{index_name}' created.")
