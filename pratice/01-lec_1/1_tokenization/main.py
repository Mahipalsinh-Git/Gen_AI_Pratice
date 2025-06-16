import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hello World"
tokens = enc.encode(text)
print("encoded: ", tokens)
print("decoded: ", enc.decode(tokens))    

