# LLM
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from rag.vectorstore import load_db_from_json_lines, load_db_from_text_document
from langchain.chains import RetrievalQA
from langchain.chains import LLMChain
from langchain import hub
from prompts import QA_CHAIN_PROMPT, SUMMARIZE_CHAPTERS, SUMMARIZE_TESTING
from langchain_community.callbacks import get_openai_callback
import time

MODEL="mistrallite:latest"

llm = Ollama(
    model=MODEL,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
    #base_url="http://172.18.48.1:11434"
)

db = load_db_from_text_document("D:\\Git\\tcc\\documents\\Emilias_podcast_99_ Anne_Lesinhovski_medium.txt",
                                 db_name='podcast_db')


qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever = db.as_retriever(),
    chain_type="stuff",
    chain_type_kwargs = { "prompt": QA_CHAIN_PROMPT },
)

#question = "O que é Emilias podcast?"
question = "Quem é o entrevistado do podcast?"

before = time.time()
print("\nSending question to the model...")
result = qa_chain({"query": question})
print(result)
print("\nTotal time spent by the model: ", time.time() - before)