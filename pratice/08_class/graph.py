from dotenv import load_dotenv
import json
from langchain_core import tools
import requests

from typing_extensions import TypedDict
from typing import Literal, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


# Hashnode API (create blog)
# calling DB is very risky? - True
# LLM as a judget
#   if calling a delete query then verify in this query where caluse is available or not like that


@tool()
def get_weather(city: str):
    """This tool returns the weather data about the given city"""

    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather iin {city} is {response.text}."

    return "something went wrong"


@tool()
def add_two_numbers(a: int, b: int):
    """This tool returns the sum of two int number"""
    return a + b


class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [get_weather, add_two_numbers]

llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools = llm.bind_tools(tools)


# node 1
def chatbot(state: State):
    messages = llm_with_tools.invoke(state["messages"])
    return {"messages": [messages]}


# node 2
tool_node = ToolNode(tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)


graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

# graph_builder.add_edge("chatbot", END) # automacally end

graph = graph_builder.compile()


def main():
    user_query = input("> ")
    messages_data = [{"role": "user", "content": user_query}]

    _state = State({"messages": messages_data})
    # graph_result = graph.invoke(_state)

    for event in graph.stream(_state, stream_mode="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()


main()
