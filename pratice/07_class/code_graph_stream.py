from typing_extensions import TypedDict
from typing import Literal
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI


load_dotenv()
client = OpenAI()


# Control by LLM
class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool


class CodeAccuracyResponse(BaseModel):
    accurecy_percentage: str


class State(TypedDict):
    user_query: str
    llm_result: str | None
    accurecy_percentage: str | None
    is_coding_question: bool | None


def classify_message(state: State):
    query = state["user_query"]

    SYSTEM_PROMPT = """ 
        You are an AI assistant. You job is to detect if the user's query is related to coding question or not.
        Return the response in specified JSON boolean only.
    """

    # Structured Outputs / Responses
    # response = client.beta.chat.completions.parse( # old
    response = client.responses.parse(  # New
        model="gpt-4.1-nano",
        text_format=ClassifyMessageResponse,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    print("classify_message: ", response.output[0].content[0].parsed.is_coding_question)
    state["is_coding_question"] = (
        response.output[0].content[0].parsed.is_coding_question
    )
    return state


def route_query(state: State) -> Literal["general_query", "coding_query"]:
    is_coding_question = state["is_coding_question"]

    if is_coding_question:
        return "coding_query"
    else:
        return "general_query"


def general_query(state: State):
    query = state["user_query"]

    SYSTEM_PROMPT = """ 
        You are an AI assistant. .
    """

    # Structured Outputs / Responses
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["llm_result"] = response.choices[0].message.content
    return state


def coding_query(state: State):
    query = state["user_query"]

    SYSTEM_PROMPT = """ 
        You are an coding expert assistant.
    """

    # Structured Outputs / Responses
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["llm_result"] = response.choices[0].message.content
    return state


def coding_validate(state: State):
    query = state["user_query"]
    llm_result = state["llm_result"]

    SYSTEM_PROMPT = f""" 
        You are expert in calculation accuracy of the code according to the question.

        user query: {query}
        code: {llm_result}
    """
    # Structured Outputs / Responses
    response = client.responses.parse(  # New
        model="gpt-4.1-nano",
        # response_format=CodeAccuracyResponse,
        text_format=CodeAccuracyResponse,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["accurecy_percentage"] = (
        response.output[0].content[0].parsed.accurecy_percentage
    )
    return state


# Graph builder
graph_builder = StateGraph(State)

graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("coding_validate", coding_validate)

graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)

graph_builder.add_edge("general_query", END)

graph_builder.add_edge("coding_query", "coding_validate")
graph_builder.add_edge("coding_validate", END)

graph = graph_builder.compile()


def main():
    user = input("> ")

    # Invoke the graph
    _state = {
        "user_query": user,
        "llm_result": None,
        "is_coding_question": False,
        "accurecy_percentage": None,
    }
    # graph_result = graph.invoke(_state)
    # print("result: ", graph_result)

    # Graph streaming
    for event in graph.stream(_state):
        print(f"Event: $event")


main()
