from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

client = OpenAI()

# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model,
)

# Vector similarity search in db


query = input("> ")
search_results = vector_db.similarity_search(query=query)

context = "\n\n".join(
    [
        f"Page Content: {result.page_content}\nPage Number: {result.metadata.get('page_label')}\nFile Location: {result.metadata.get('source')}"
        for result in search_results
    ]
)


SYSTEM_PROMPT = f"""

You are a helpful AI Assistant who answers user query based on the available context retrived from a PDF file along
with page_contents and page number.

You should only ans the user based on the following context and navigate the user to open the right page number to know more.

Context:
{context}
"""

# print("system prompt:", SYSTEM_PROMPT)

messages = []

response = client.chat.completions.create(
    model="gpt-4.1-mini-2025-04-14",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ],
)

print("🤖 ", response.choices[0].message.content)
