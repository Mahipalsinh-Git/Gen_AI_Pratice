# Tokenization
import tiktoken

# To get the tokeniser corresponding to a specific model in the OpenAI API:
enc = tiktoken.encoding_for_model("gpt-4o")

text = "hello world"
tokens = enc.encode(text)
print("encode token: ", tokens)

decoded = enc.decode(tokens)
print("decode token: ", decoded)
