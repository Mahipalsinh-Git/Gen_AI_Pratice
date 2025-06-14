from email import message
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

# chain-of-thought prompt:
SYSTEM_PROMPT = """
    You are a helpful AI assistant who is specialized in resolving user query.
    You work on START, PLAN, ACTION and OBSERVE mode.
    For the given user input, analyes the input and break down the problem step by step.
    The steps are you get a user input, you analyse, you think, you think again, and think for severval times and then return to an outcome with an explanation.

    Follow the steps in sequence that is "analyse", "think", "output", "validate", if output wrong then "think again", "validate" until finalize the accurate "result".

    Rules:
        1. Follow the strict JSON output as per schema.
        2. Always perform one step at a time and wait for the next input.
        3. Carefully analyse the user query.

    Output Format:
        {{"step": "string", "content": "string"}}

    Example:
        Input: what is 2 + 2
        Output: {{"step":"analyse", "content": "Alright! The user is interest in maths query and he is asking a basic mathmetic operation."}}
        Output: {{"step":"think", "content": "To perform this addition, I must go left to right and all the operands."}}
        Output: {{"step":"output", "content": "4"}}
        Output: {{"step":"validate", "content": "Seems like 4 is correct answer for 2 + 2"}}
        Output: {{"step":"think again", "content": "if 4 is not correct answer then re-think, how to solve this issue}}
        Output: {{"step":"validate", "content": "verify after thinking answer is correct or not}}
        Output: {{"step":"result", "content": "2 + 2 = 4 and this is calculated by adding all the numbers}}
"""

message = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {
        "role": "user",
        "content": "what is the avg of sum of 2 and 3 multiplied by 5 divided by 2",
    },
]

# query = input("> ")
# message.append(
#     {"role": "user", "content": query},
# )

while True:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=message,
    )

    parsedJson = json.loads(response.choices[0].message.content)

    message.append(
        {"role": "assistant", "content": json.dumps(parsedJson)},
    )

    if parsedJson.get("step") != "result":
        print("🧠: ", parsedJson.get("content"))
        continue

    print("🤖: ", parsedJson.get("content"))
    break
