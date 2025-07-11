from httpx import request
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()
client = OpenAI()


def run_command(cmd: str):
    result = os.system(cmd)
    return result


def get_weather(city: str):
    # url = f"https://wttr.in{city}?format=%C+%t"

    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather iin {city} is {response.text}."


available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
}

SYSTEM_PROMPT = """
    You are a helpful AI assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the tool selection you perform an action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
     - Follow the output JSON Format
     - Always perform one step at a time and wait for next input
     - Carefully analyse the user query

    Output JSON Format:
        {{
            "step": "string",
            "content": "string",
            "function": "The name of function if the step is action",
            "input": "The input paramater for the function",
        }}

    Available Tools:
        - "get_weather": Takes a city name as an input and returns the current weather for the city
        - "run_command": Takes linux command as a string and executes the command and returns the output after executing it.

    Example:
    User: what is the weather of new york?
    output: {{"step": "plan", "content": "The user is interested in weather data of new york."}}
    output: {{"step": "plan", "content": "From the available tools i should call get_weather"}}
    output: {{"step": "action", "function": "get_weather", "input":"new york"}}
    output: {{"step": "observe", "output": "12 Degree cel"}}
    output: {{"step": "output", "content": "The weather for new york seems to be 12 degree."}}
"""

chatMessages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    },
]

while True:
    user_input = input("> ")
    chatMessages.append(
        {"role": "user", "content": user_input},
    )

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1",
            response_format={"type": "json_object"},
            messages=chatMessages,
        )

        chatMessages.append(
            {"role": "assistant", "content": response.choices[0].message.content},
        )

        parsed_response = json.loads(response.choices[0].message.content)
        if parsed_response.get("step") == "plan":
            print("🧠: ", parsed_response.get("content"))
            continue

        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print(f"🛠️: Calling Tool:{tool_name} with input {tool_input}")

            if available_tools.get(tool_name) != False:
                output = available_tools[tool_name](tool_input)
                chatMessages.append(
                    {
                        "role": "user",
                        "content": json.dumps({"step": "observe", "output": output}),
                    }
                )
                continue

        if parsed_response.get("step") == "output":
            print("🤖: ", parsed_response.get("content"))
            break
