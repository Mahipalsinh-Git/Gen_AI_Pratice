# https://langchain-ai.github.io/langgraph/how-tos/persistence/?h=mongo#use-in-production

from pydantic import config
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import StateGraph, START, END, add_messages
from openai import OpenAI
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()

llm = init_chat_model(model_provider="openai", model="gpt-4.1")


class State(TypedDict):
    messages: Annotated[list, add_messages]


# Node
def chat_bot(state: State):

    response = llm.invoke(state["messages"])
    return {"messages": [response]}


# Graphbuilder
graph_builder = StateGraph(State)
graph_builder.add_node("chat_bot", chat_bot)

# Edges
graph_builder.add_edge(START, "chat_bot")
graph_builder.add_edge("chat_bot", END)

# Create Graph
# graph = graph_builder.compile()


def compile_graph_with_checkpointer(checkpointer):
    compile_graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return compile_graph_with_checkpointer


def main():

    DB_URI = "mongodb://admin:admin@localhost:27017"
    config = {"configurable": {"thread_id": "1"}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)

        query = input("> ")

        # Invoke the graph
        _state = {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }

        # graph_result = graph.invoke(_state)
        graph_result = graph_with_mongo.invoke(_state, config)
        print("graph result:", graph_result)


main()
