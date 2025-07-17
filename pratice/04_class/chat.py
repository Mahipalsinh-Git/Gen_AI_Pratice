from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()
client = OpenAI()

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning_vectors",
)

user_query = input("> ")

# vector similarity search in db
search_result = vector_store.similarity_search(query=user_query)

context = "\n\n\n".join(
    [
        f"Page content: {result.page_content}\n Page number: {result.metadata['page_label']}\nFile location: {result.metadata['source']}"
        for result in search_result
    ]
)


SYSTEM_PROMPT = f"""
    You are a helpful AI Assistant who answers user query based on the available context retrieved from a PDF file along with page_contents and page number. 
    You should only answer the user based on the following context and navigate the user to open the right page number to know more.

    Context:
    {context}
"""
# print("Prompt", SYSTEM_PROMPT)

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_query,
        },
    ],
)

print("🤖 ", response.choices[0].message.content)
