import os
from elasticsearch import Elasticsearch
from langchain_community.document_loaders import PyPDFLoader
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from share.slack.util.logger import setup_logger

from elastic_client import ElasticClient

logger = setup_logger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))


class PdfStore(object):
    host = ElasticClient().elasticsearch_url
    elasticsearch_client = Elasticsearch(hosts=[host])
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,  # 더 큰 청크 사이즈
            chunk_overlap=200,  # 더 큰 오버랩
            length_function=len,
            separators=["\n\n", "\n", " ", ""],  # 문장 단위로 분할
        )

    def get_store(self, index_name: str):
        return ElasticsearchStore(
            index_name=index_name,
            embedding=self.embedding,
            es_url=self.host,
        )

    def get_retriever(self, index_name):
        return self.get_store(index_name).as_retriever(search_kwargs={"k": 3})

    def embedding_pdf(self, index_name: str, file_name: str):
        try:
            file_path = os.path.join(current_dir, "../data", file_name)
            loader = PyPDFLoader(file_path)
            documents = loader.load()

            # 문서 분할
            splits = self.text_splitter.split_documents(documents)
            logger.info(f"문서 분할 완료: {len(splits)}개 청크 생성")

            # 배치 처리
            batch_size = 50  # 더 큰 배치 사이즈
            store = self.get_store(index_name)

            for i in range(0, len(splits), batch_size):
                batch = splits[i : i + batch_size]
                try:
                    # 각 문서의 메타데이터 정리
                    processed_batch = []
                    for doc in batch:
                        try:
                            # 메타데이터 정리
                            doc.metadata = {
                                k: str(v)
                                for k, v in doc.metadata.items()
                                if v is not None
                                and len(str(v)) < 1000  # 메타데이터 제한 완화
                            }
                            processed_batch.append(doc)
                        except Exception as e:
                            logger.warning(f"문서 메타데이터 처리 중 오류: {str(e)}")
                            continue

                    if processed_batch:
                        store.add_documents(documents=processed_batch)
                        logger.info(f"배치 처리 완료: {len(processed_batch)}개 문서")

                except Exception as e:
                    logger.error(f"배치 처리 중 오류 발생: {str(e)}")
                    continue

            logger.info(f"PDF 임베딩 완료: 총 {len(splits)}개 청크 처리됨")

        except Exception as e:
            logger.error(f"PDF 임베딩 실패: {str(e)}")
            raise
