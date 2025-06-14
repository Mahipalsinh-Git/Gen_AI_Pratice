from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses import response
import numpy as np

load_dotenv()

client = OpenAI()

text = "Hello World, Mahipal how are you?"

# response = client.embeddings.create(
#     model="text-embedding-3-small",
#     input=text
# )

# print("Vector embeddings: ", response) 
# print("Vector embeddings length: ", len(response.data[0].embedding))

# Start a fine-tune job on your custom chai recipes dataset
# /Users/mahipal/Work/Course/GenAI/Cohort_2/lec_1/2_vector_embedding/file-abc123.jsonl


# Get embeddings for two tea descriptions
resp1 = client.embeddings.create(model="text-embedding-3-small", input="Spicy masala tea")
resp2 = client.embeddings.create(model="text-embedding-3-small", input="Ginger tea")

emb1 = np.array(resp1.data[0].embedding)
emb2 = np.array(resp2.data[0].embedding)

# Compute cosine similarity
cosine_sim = emb1.dot(emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
print(f"Similarity between Masala Tea 🥣 and Ginger Tea 🌿: {cosine_sim:.3f}")

# file_response = client.files.create(
#   file=open("lec_1/2_vector_embedding/file-abc123.jsonl", "rb"),
#   purpose="fine-tune"
# )

# print("File created with ID:", file_response.id)


# response = client.fine_tuning.jobs.create(
#   training_file=file_response.id,
#   model="gpt-3.5-turbo"
# )

# print("Fine-tune job created with ID:", response)

# response = client.chat.completions.create(
#     model="gpt-3.5-turbo",   # Modern chat model
#     messages=[{
#         "role": "user",
#         "content": "Brew me a vanilla-cinnamon chai recipe."
#     }],
#     temperature=0.7,
#     max_tokens=100
# )

# print("Chef’s new recipe:\n", response.choices[0].message.content)