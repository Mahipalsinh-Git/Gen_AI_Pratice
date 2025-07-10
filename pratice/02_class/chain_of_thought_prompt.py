from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI()

# Chain of thought prompting: The model is encouraged to break down reasoning step by step before arriving at a answer.
SYSTEM_PROMPT = """ 
    You are an helpful AI assistant who is specialize in resolving user query.
    You work on START, PLAN, ACTION and OBSERVE Mode.
    For the given user input, analyse the input and bread down the problem step by step.

    The stpes are you get a user input, you analyse, you think, you think again, and think for several times and then return the output with an explanatation.
    
    Follow the steps in sequence that is "analyse", "think", "output", "validate" and finally "result".

    Rules:
    1. Follow the strict JSON output as per schema.
    2. Always perform one step at a time and wait for the next input.
    3. Carefully analyse the user query.

    Output format:
    {{"step": "string", "content": "string"}}

    Examples:
    Input: what is 2 + 2
    Output: {{"step": "analyse", "content": "Alrigh! The user is interest in maths query and he is asking a basic arthematic operation"}}
    Output: {{"step": "think", "content": "To perform this addition, I must go from left to right and all the operands."}}
    Output: {{"step": "output", "content": "4"}}
    Output: {{"step": "validate", "content": "Seems like 4 is correct answer for 2 + 2"}}
    Output: {{"step": "result", "content": "See2 + 2 = 4 and this is calculated by adding all numbers."}}

"""

message = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "what is 5 / 2 * 3 to power 4"},
]

while True:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=message,
        response_format={
            "type": "json_object",
        },
    )
    message.append(
        {"role": "assistant", "content": response.choices[0].message.content}
    )

    parsed_response = json.loads(response.choices[0].message.content)

    if parsed_response.get("step") == "result":
        print("👨🏻‍💻 ", parsed_response.get("content"))
        break

    print("🤖 ", parsed_response.get("content"))
