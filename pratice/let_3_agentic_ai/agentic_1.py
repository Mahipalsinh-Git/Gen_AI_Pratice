from dotenv import load_dotenv
from openai import OpenAI
import json
import requests
import os
import subprocess
import anthropic


load_dotenv()

client = OpenAI()
anthropic_client = anthropic.Anthropic()


def run_command(cmd: str) -> str:
    try:
        output = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        )
        return output.strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip() or f"Command failed with exit code {e.returncode}"


def get_weather(city: str):
    print("location: ", city)

    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."

    return "Something went wrong"


available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
}

SYSTEM_PROMPT = """
    You are a helpful AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool and on the tool selection you perform an action to call the tool.

    wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
        - Follow the output JSON format.
        - Always perform one step at a time and wait for next input
        - Carefully analyse the user query

    Available Tools:
        - "get_weather" : Takes a city name as an input and returns the current weather for the city
        - "run_command" : Takes linux command as string and execute the command and returns the output after executing it. 

    Example:
        user: what is the weather of new york?
        output: {{"step": "plan", "content": "The user is interested in weather data of new york"}}
        output: {{"step": "plan", "content": "From the available tools i should call get_weather"}}
        output: {{"step": "action", "function": "get_weather ", "input": "new york"}}
        output: {{"step": "observe", "output": "12 degree cel"}}
        output: {{"step": "output", "content": "The weather for new york seems to be 12 degree."}}

"""
messages = [
    # {
    #     "role": "system",
    #     "content": SYSTEM_PROMPT,
    # }
]

try:
    while True:
        user_query = input("< ")
        messages.append(
            {
                "role": "user",
                "content": user_query,
            }
        )

        while True:
            # response = client.chat.completions.create(
            #     model="gpt-4.1-2025-04-14",
            #     response_format={"type": "json_object"},
            #     messages=messages,
            # )

            response = anthropic_client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=1000,
                temperature=1,
                system=SYSTEM_PROMPT,
                messages=messages,
            )

            parsedJson = json.loads(response.choices[0].message.content)
            print("🧠: ", parsedJson)

            messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps(parsedJson),
                },
            )

            if parsedJson.get("step") == "plan":
                continue

            if parsedJson.get("step") == "action":
                tool_name = parsedJson.get("function")
                tool_input = parsedJson.get("input")

                print(f"🛠️: Calling Tool: {tool_name} with input {tool_input}")

                if available_tools.get(tool_name) != False:
                    output = available_tools[tool_name](tool_input)
                    messages.append(
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "step": "observe",
                                    "output": output,
                                }
                            ),
                        }
                    )
                    continue

            if parsedJson.get("step") == "output":
                print("🤖: ", parsedJson.get("content"))
                break
except Exception as e:
    print("An error occurred!", e)
