from unittest import result
from dotenv import load_dotenv
from mem0 import Memory
from openai import OpenAI
import os
import json

# Disable posthog tracking
# try:
#     import posthog

#     posthog.disabled = True
#     posthog.api_key = None
#     posthog.host = None
#     posthog.capture = lambda *args, **kwargs: None
# except ImportError:
#     pass

"""
Best approch
    last 50 messages AI summary
    + last 20 message
    + memory
    + user_query

    user memory in queue - because heavy part

    http://localhost:7474/browser/preview/
    http://localhost:6333/dashboard#/collections/mem0
"""

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["MEM0_DISABLE_TELEMETRY"] = "true"

client = OpenAI()

config = {
    "version": "v1.1",
    "telemetry": {"enabled": False},
    "embedder": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "text-embedding-3-small"},
    },
    "llm": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4.1"},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": "6333"},  # local
        # "config": {"host": "vector-db", "port": "6333"}, # server
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            # "url": "neo4j+s://xxx",
            # "url": "bolt://neo4j", # server
            "url": "bolt://localhost:7687",  # local
            "username": "neo4j",
            "password": "reform-william-center-vibrate-press-5829",
        },
    },
}

mem_client = Memory.from_config(config)


def chat():
    while True:
        user_query = input("> ")

        # all_memories = mem_client.get_all(user_id="mahipal") # fetch all memories
        relevant_memories = mem_client.search(query=user_query, user_id="mahipal")

        memories = [
            f'ID: {mem.get("id")} Memory: {mem.get("memory")}'
            for mem in relevant_memories.get("results")
        ]

        SYSTEM_PROMPT = f"""
            You are an memory aware assistant which reponds to user with context.
            you are given with past memories and facts about the user.

            Memory of the user:
            {json.dumps(memories)} 
        """

        result = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ],
        )

        print(f"🤖: {result.choices[0].message.content}")
        mem_client.add(
            [
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": result.choices[0].message.content},
            ],
            user_id="mahipal",  # user db id
        )


chat()
