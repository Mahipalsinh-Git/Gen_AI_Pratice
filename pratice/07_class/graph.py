from typing_extensions import TypedDict
from typing import Literal, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_openai import ChatOpenAI

load_dotenv()
# client = OpenAI()

llm = init_chat_model(model_provider="openai", model="gpt-4.1")


# with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:

#     def call_model(state: MessagesState):
#         response = model.invoke(state["messages"])
#         return {"messages": response}

#     builder = StateGraph(MessagesState)
#     builder.add_node(call_model)
#     builder.add_edge(START, "call_model")

#     graph = builder.compile(checkpointer=checkpointer)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chat_node(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


# Graph builder
graph_builder = StateGraph(State)

graph_builder.add_node("chat_node", chat_node)

graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)

graph = graph_builder.compile()


def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer


def main():

    # Mongodb format
    #   mongodb://<username>:<pass>@<host>:<port>
    DB_URI = "mongodb://admin:admin@localhost:27017"
    config = {"configurable": {"thread_id": 1}}

    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)

        query = input("> ")
        messages_data = [{"role": "user", "content": query}]

        # Invoke the graph
        _state = {"messages": messages_data}
        graph_result = graph_with_mongo.invoke(_state, config)
        print("result: ", graph_result)


main()
