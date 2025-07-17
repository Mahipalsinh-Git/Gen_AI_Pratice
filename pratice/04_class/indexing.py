# RAG - Retrieval Augmented Generation

from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore


load_dotenv()

file_path = Path(__file__).parent / "mcp.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()  # Read PDF file
# print("docs", docs[0])  # verify

# Chunking / Splitting

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

split_docs = text_splitter.split_documents(documents=docs)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    # With the `text-embedding-3` class
    # of models, you can specify the size
    # of the embeddings you want returned.
    # dimensions=1024
)
# Using [embedding_model] create embedding of [split_docs] and store in DB

vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="learning_vectors",
)

print("Indexing of documents done...")
