from dotenv import load_dotenv
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


def run_embedding():
    data_file = "./data/tiger-nasdaq100-coveredcall.pdf"

    loader = PDFPlumberLoader(file_path=data_file)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    split_docs = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = ElasticsearchStore(
        es_url="http://172.16.120.203:9201",
        index_name="sylee_tiger_etf",
        embedding=embeddings,
    )

    vector_store.add_documents(split_docs)


if __name__ == "__main__":
    run_embedding()
