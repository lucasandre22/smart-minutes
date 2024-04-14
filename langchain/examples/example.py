from langchain_community.llms import Ollama
llm = Ollama(model="mistrallite") #32k context window

from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are world class technical documentation writer."),
    ("user", "{input}")
])
chain = prompt | llm 
print(chain.invoke({"input": "how can langsmith help with testing?"}))