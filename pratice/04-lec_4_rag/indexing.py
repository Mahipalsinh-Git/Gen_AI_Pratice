# RAG - Retrieval augmented generation
# How to do optimal RAG?
#   Chunking - Paragraph wise
#   Prompt - Available data + prompt => LLM
#   Ingestion / Indexing
#       Step 1: chunking/splitting
#       Step 2: store chunk to vector database
#   Retrival
#       User query - convert into vector
#       search into vector database
#       Pinecode, AstraDB, Chroma DB, Milvus, PG Vector, weaviate, QDrant DB

from openai import OpenAI
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

# Loading
pdf_path = Path(__file__).parent / "nodejs.pdf"

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()  # Read PDF file

# print("docs", docs[0])
print("Loading done...")

# Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400,
    # length_function=len,
    # is_separator_regex=False,
)

split_docs = text_splitter.split_documents(documents=docs)

print("Chunking done...")

# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    # With the `text-embedding-3` class
    # of models, you can specify the size
    # of the embeddings you want returned.
    # dimensions=1024
)

print("Vector Embeddings done...")
# Using embedding_model create embeddings of split_docs and store in DB

vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning_vectors",
)

print("Indexing of documents done...")
