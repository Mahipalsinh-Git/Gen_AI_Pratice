# Agentic workflow
# LLM as judgef


from unittest import result
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal

load_dotenv()

client = OpenAI()


class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool


class CodeAccuracyResponse(BaseModel):
    accuracy_percentage: str


class State(TypedDict):
    user_query: str
    llm_result: str | None
    accuracy_percentage: str | None
    is_coding_question: bool | None


def classify_message(state: State):
    query = state["user_query"]

    SYSTEMT_PROMPT = """
                    You are an AI assistant. Your job is to detect if the user's query is related to coding question or not.
                    Return the response in specified JSON boolean only
                    """

    # Structured output / response
    response = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ClassifyMessageResponse,
        messages=[
            {
                "role": "system",
                "content": SYSTEMT_PROMPT,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
    )

    is_coding_question = response.choices[0].message.parsed.is_coding_question
    state["is_coding_question"] = is_coding_question

    return state


def route_query(state: State) -> Literal["general_query", "coding_query"]:
    is_coding_question = state["is_coding_question"]

    if is_coding_question:
        return "coding_query"

    return "general_query"


def general_query(state: State):
    query = state["user_query"]

    SYSTEMT_PROMPT = "You are an helpful AI assistant. Your job is resolve user query"

    # Structured output / response
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        # response_format=ClassifyMessageResponse,
        messages=[
            {
                "role": "system",
                "content": SYSTEMT_PROMPT,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
    )

    result = response.choices[0].message.content
    state["llm_result"] = result

    return state


def coding_query(state: State):
    query = state["user_query"]

    SYSTEMT_PROMPT = (
        "You are an helpful AI coding assistant. Your job is resolve user coding query"
    )

    # Structured output / response
    response = client.chat.completions.create(
        model="gpt-4.1",
        # response_format=ClassifyMessageResponse,
        messages=[
            {
                "role": "system",
                "content": SYSTEMT_PROMPT,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
    )

    result = response.choices[0].message.content
    state["llm_result"] = result

    return state


def coding_validate(state: State):
    query = state["user_query"]
    llm_code = state["llm_result"]

    SYSTEM_PROMPT = f"""
        You are expert in calculating accuracy of the code according to the question.
        Return the percentage of accuracy
        
        User Query: {query}
        Code: {llm_code}
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4.1",
        response_format=CodeAccuracyResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    state["accuracy_percentage"] = response.choices[
        0
    ].message.parsed.accuracy_percentage
    return state


graph_builder = StateGraph(State)

# Define nodes
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("coding_validate", coding_validate)


# Define branch
graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)
graph_builder.add_edge("general_query", END)
graph_builder.add_edge("coding_query", "coding_validate")
graph_builder.add_edge("coding_validate", END)

# Create Graph
graph = graph_builder.compile()


def main():
    user = input("> ")

    # Invoke the graph
    _state: State = {
        "user_query": user,
        "accuracy_percentage": None,
        "is_coding_question": False,
        "llm_result": None,
    }

    graph_result = graph.invoke(_state)
    print("graph result:", graph_result)


main()
