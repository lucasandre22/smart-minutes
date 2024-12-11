from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from llms.ollama.ollama_llm import Ollamallm
from core.config import CONFIG
from .summarization import Summarization
from .template_refine import *

"""Refine chain.

The refine documents chain constructs a response by looping over the input documents
and iteratively updating its answer.
"""

class SummarizationRefine(Summarization):
    """Summarization that uses refine method:
    Splits up a document or text into chunks, update a rolling summary be iterating over the documents in a sequence.
    """
    def __init__(self, llm: Ollamallm,
                 refine_prompt=SummarizationRefinePrompts.refine_prompt_default(),
                 question_prompt=SummarizationRefinePrompts.question_prompt_default()):
        Summarization.__init__(self,
            load_summarize_chain(
                llm, 
                chain_type="refine", 
                question_prompt=question_prompt,
                refine_prompt=refine_prompt, 
                document_variable_name="text", 
                initial_response_name="existing_answer"
            )
        )
        self.llm = llm

    #TODO: organize the summary in a timeline
    def organize_summary():
        pass

if __name__ == "__main__":
    LLM = Ollama(
        model=CONFIG.model,
        verbose=True,
        temperature=0,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        #top_k=5
    )
    file = "..\\documents\\ppgca\\transcript_talkers.txt"

    summarization_refine = SummarizationRefine(LLM)
    docs = summarization_refine.chunk_file_into_documents(file, 1024)
    print(len(docs))
    docs = summarization_refine.chunk_file_into_documents("databases\\transcripts\\Reunião do Colegiado do PPGCA – 2024_09_30 13_22 BRT – Recording-pt-1.csmt", 1024)
    print(len(docs))

    result = summarization_refine.invoke(docs)

    print(result["output_text"])