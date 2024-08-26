# LLM
from rag.vectorstore import load_db_from_text_document
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain import hub
from prompts import QA_LLAMA3_CHAIN_PROMPT
import time

MODEL="llama3:latest"

llm = ChatOllama(model=MODEL, format="json", temperature=0)

db = load_db_from_text_document("D:\\Git\\tcc\\documents\\Emilias_podcast_99_ Anne_Lesinhovski_medium.txt",
                                 db_name='podcast_db')

retriever = db.as_retriever()

retrieval_grader = QA_LLAMA3_CHAIN_PROMPT | llm | JsonOutputParser()

#question = "Quem é o entrevistado do podcast?"
#question = "Qual é o assunto do podcast?"
question = "Qual é o assunto tratado nesse episódio do podcast?"
docs = retriever.invoke(question)

#Strategy: See if the document it is relevant before sending to the model
#doc_txt = docs[1].page_content

before = time.time()
print("\nSending question to the model...")
response = retrieval_grader.invoke({"question": question, "document": docs})
print(response)
print("\nTotal time spent by the model: ", time.time() - before)