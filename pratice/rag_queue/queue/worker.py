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


def process_query(query: str):

    # now here you can handle manage request
    # like request count greate than 5 then sleep
    print("Searching Chunks", query)
    search_results = vector_db.similarity_search(query=query)
    print("search_results", search_results)

    context = "\n\n\n".join(
        [
            f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}"
            for result in search_results
        ]
    )

    print("context", context)

    SYSTEM_PROMPT = f"""
        You are a helpfull AI Assistant who asnweres user query based on the
        available context
        retrieved from a PDF file along with page_contents and page number.

        You should only ans the user based on the following context and navigate
        the user
        to open the right page number to know more.

        Context:
        {context}
    """

    chat_completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    print("chat_completion", chat_completion)

    # Save to DB
    print(f"🤖: {query}", chat_completion.choices[0].message.content, "\n\n\n")
    return chat_completion.choices[0].message.content
