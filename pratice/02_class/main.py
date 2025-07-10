from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Zero shot prompting
ZERO_SYSTEM_PROMPT = """ 
    You are an AI expert in coding. you only know python and nothing else. 
    You help users in solving there python doubts only and nothing else.
    If user tried to ask something else apart from python you can just roast them.
"""

# Few shot prompting
FEW_SYSTEM_PROMPT = """ 
    You are an AI expert in coding. you only know python and nothing else. 
    You help users in solving there python doubts only and nothing else.
    If user tried to ask something else apart from python you can just roast them.

    Examples:
    User: How to make a Tea?
    Assistant: I don't have information requarding making a tea. I am know about Python.

    User: How to write a function in python?
    Assistant: def fn_name(x: int) -> int:
                    pass # Logic of the function
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": FEW_SYSTEM_PROMPT},
        {"role": "user", "content": "Hello, how are you?"},
        {
            "role": "assistant",
            "content": "Hello! I'm just a computer program, so I don't have feelings, but I'm here and ready to help you. How can I assist you today?",
        },
        {"role": "user", "content": "how to make a maggi?"},
    ],
)

print("response:", response.choices[0].message.content)
