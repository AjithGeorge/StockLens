from langchain_ollama import ChatOllama


llm = ChatOllama(model="qwen2:7b")


messages = [
    ("system", "You are a helpful translator. Translate the user sentence to French."),
    ("human", "I love programming."),
]
response = llm.invoke(messages)
print(response)
