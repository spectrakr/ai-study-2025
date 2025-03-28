from dotenv import load_dotenv
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

file_name = "CleanCode20pages.pdf"

def run_embedding():
    loader = PDFPlumberLoader(
        file_path="./data/CleanCode20pages.pdf"
    )
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

    split_docs = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vector_store = ElasticsearchStore(
        es_url="http://172.16.120.203:9201",
        index_name="ygna_pdf",
        embedding=embeddings,
    )
    vector_store.add_documents(split_docs)


if __name__ == "__main__":
    run_embedding()
