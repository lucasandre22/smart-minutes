from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from src.llms.ollama.ollama_llm import Ollamallm
from src.summarization.utils import chunk
from .summarization import Summarization
from .template_map_reduce import *

"""Map-reduce chain.

Splits up a document or text into chunks, sends the smaller parts to the LLM with one prompt,
then combines the results with another prompt.
"""

class SummarizationMapReduce(Summarization):
    """Summarization that uses Map-reduce:
    Splits up a document or text into chunks, summarize each chunk in a "map" step and then "reduce" the summaries into a final summary.
    """
    def __init__(self, llm: Ollamallm,
                 map_prompt=SummarizationMapReducePrompts.map_prompt_default(),
                 combine_prompt=SummarizationMapReducePrompts.combine_prompt_default()):
        Summarization.__init__(self,
            load_summarize_chain(
                llm,
                chain_type="map_reduce",
                map_prompt = map_prompt,
                combine_prompt=combine_prompt,
                combine_document_variable_name="text",
                map_reduce_document_variable_name="text"
            )
        )
        self.llm = llm

if __name__ == "__main__":
    MODEL="lucasalmeida/gemma-2-9b-it-sppo-iter3:Q4_K_M"
    LLM = Ollama(
        model=MODEL,
        verbose=True,
        temperature=0,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        #top_k=5
    )
    file = ".\\documents\\ppgca\\transcript_talkers.txt"

    summarization_refine = SummarizationMapReduce(LLM)
    docs = summarization_refine.chunk_file_into_documents(file)
    print(len(docs))

    result = summarization_refine.invoke(docs)

    print(result["output_text"])