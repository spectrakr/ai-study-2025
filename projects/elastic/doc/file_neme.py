from pydantic import BaseModel

from elastic_client import ElasticClient
from share.slack.util.logger import setup_logger

logger = setup_logger(__name__)


class FileName(BaseModel):
    file_name: str
    real_file_name: str


class FileNameStore(object):
    index_name = "file_name"

    def __init__(self):
        ElasticClient.create_index(self.index_name)

    def get_real_name(self, file_name) -> str:
        res = ElasticClient.get(index_name=self.index_name, doc_id=file_name)
        if res is None:
            return file_name
        return FileName(**res).real_file_name

    def add_docs(self, real_file_name: str, file_name: str):
        logger.info(f" saved file {file_name} : {real_file_name }")
        ElasticClient.upsert_doc(
            index=self.index_name,
            _id=file_name,
            doc=dict(
                FileName(
                    file_name=file_name,
                    real_file_name=real_file_name,
                )
            ),
        )

    def delete_doc(self, index_name):
        ElasticClient.delete_doc(self.index_name, index_name)


if __name__ == "__main__":
    store = FileNameStore()
    # store.add_docs("seoklee_baseball", "당신은 야구 전문가 AI 입니다.")
    # store.delete_doc("default_pdf_index")
    print(store.get_real_name("doc_20250401_002344_cfb26945.pdf"))
