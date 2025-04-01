from pydantic import BaseModel

from elastic_client import ElasticClient
from share.slack.util.logger import setup_logger

logger = setup_logger(__name__)


class EmbeddedDocs(BaseModel):
    index_name: str
    prompt: str
    file_names: list[str]


class IndexPromptStore(object):
    index_name = "seoklee_index_prompt"

    def __init__(self):
        ElasticClient.create_index(self.index_name)

    def _get(self, index_name):
        return ElasticClient.get(index_name=self.index_name, doc_id=index_name)

    def add_docs(self, index_name, prompt, file_name: str):
        found_doc = self._get(index_name)
        file_names = [file_name]
        if not found_doc is None:
            logger.debug(EmbeddedDocs(**found_doc).file_names)
            file_names.extend(EmbeddedDocs(**found_doc).file_names)

        ElasticClient.upsert_doc(
            index=self.index_name,
            _id=index_name,
            doc=dict(
                EmbeddedDocs(
                    index_name=index_name, prompt=prompt, file_names=file_names
                )
            ),
        )

    def delete_doc(self, index_name):
        ElasticClient.delete_doc(self.index_name, index_name)

    def get_all_docs(self) -> list[EmbeddedDocs]:
        return [
            EmbeddedDocs(**doc) for doc in ElasticClient.get_all_docs(self.index_name)
        ]


if __name__ == "__main__":
    store = IndexPromptStore()
    # store.add_docs("seoklee_baseball", "당신은 야구 전문가 AI 입니다.")
    store.delete_doc("default_pdf_index")
