# from openai import OpenAI
# from dotenv import load_dotenv

from openai import OpenAI
from dotenv import load_dotenv
from openai.types.responses import response

load_dotenv()
client = OpenAI()

text = "dog chases cat"

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text,
)

print("response: ", response.data[0].embedding)
