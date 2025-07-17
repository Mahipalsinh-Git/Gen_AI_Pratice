from dotenv import load_dotenv
import json

from typing_extensions import TypedDict
from typing import Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt, Command

from langchain_core.tools import tool
from langchain.chat_models import init_chat_model

load_dotenv()


@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt(
        {"query": query}
    )  # this saved the state in dB and kills the graph
    return human_response["data"]  # resume from here


class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [human_assistance]

llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools = llm.bind_tools(tools)


def chat_node(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


tools = ToolNode(tools)


# Graph builder
graph_builder = StateGraph(State)

graph_builder.add_node("chat_node", chat_node)
graph_builder.add_node("tools", tools)

graph_builder.add_edge(START, "chat_node")
graph_builder.add_conditional_edges("chat_node", tools_condition)
graph_builder.add_edge("chat_node", END)


def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer


def user_chat():

    # Mongodb format
    #   mongodb://<username>:<pass>@<host>:<port>
    DB_URI = "mongodb://admin:admin@localhost:27017"
    config = {"configurable": {"thread_id": 22}}

    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)

        while True:
            query = input("> ")
            messages_data = [{"role": "user", "content": query}]

            # Invoke the graph
            _state = {"messages": messages_data}

            for event in graph_with_mongo.stream(_state, config, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()


user_chat()


# def admin_call():
#     # Mongodb format
#     #   mongodb://<username>:<pass>@<host>:<port>
#     DB_URI = "mongodb://admin:admin@localhost:27017"
#     config = {"configurable": {"thread_id": 20}}

#     with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
#         graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)

#         state = graph_with_mongo.get_state(config)
#         last_message = state.values["messages"][-1]

#         tool_calls = last_message.additional_kwargs.get("tool_calls", [])

#         user_query = None

#         for call in tool_calls:
#             if call.get("function", {}).get("name") == " ":
#                 args = call["function"].get("arguments", "{}")
#                 try:
#                     args_dict = json.loads(args)
#                     user_query = args_dict.get("query")
#                 except json.JSONDecodeError:
#                     print("Failed to decode function arguments.")

#             print("User has a query: ", user_query)

#             solutions = input("> ")

#             resume_command = Command(resume={"data": solutions})

#             for event in graph_with_mongo.stream(
#                 resume_command, config, stream_mode="values"
#             ):
#                 if "messages" in event:
#                     event["messages"][-1].pretty_print()


#  admin_call()
