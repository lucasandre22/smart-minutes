# LLM
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from vectorstore import load_db_from_json_lines
import time
from prompts import QA_CHAIN_PROMPT

MODEL="llama2:7b"
#MODEL="mistrallite"

llm = Ollama(
    model = MODEL,
    verbose = True,
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]),
    #base_url="http://172.18.48.1:11434"
)

# QA chain
from langchain.chains import RetrievalQA
from langchain import hub

db = load_db_from_json_lines("/mnt/d/Git/tcc/documents/Emilias_podcast_99_ Anne_Lesinhovski_small.jsonl",
                                 db_name='podcast',
                                 jq_schema=".content")

# LangChain Hub is a repository of LangChain prompts shared by the community
#QA_CHAIN_PROMPT = hub.pull("rlm/rag-prompt-llama")
qa_chain = RetrievalQA.from_chain_type(
    llm,
    # we create a retriever to interact with the db using an augmented context
    retriever = db.as_retriever(), 
    chain_type_kwargs = {"prompt": QA_CHAIN_PROMPT},
)
question = "Qual é o objetivo do podcast?"

before = time.time()
result = qa_chain({"query": question})

print("\nTotal time spent by the model: ", time.time() - before)