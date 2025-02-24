from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from src.llms.ollama.ollama_llm import Ollamallm
from src.summarization.utils import chunk
from .summarization import Summarization
from .template_map_reduce import *

"""
Map-reduce chain.

Splits up a document or text into chunks, sends the smaller parts to the LLM with one prompt,
then combines the results with another prompt.
"""

class SummarizationMapReduce(Summarization):
    """
    A class for performing summarization using the map-reduce method.

    This class extends `Summarization` to implement a summarization chain that first splits a document or text into smaller
    chunks, summarizes each chunk in the "map" step, and then combines the individual summaries into a final summary during the "reduce" step.

    Attributes:
        llm (Ollamallm): The language model used for summarization.
    
    Methods:
        __init__(self, llm: Ollamallm, map_prompt: str, combine_prompt: str):
            Initializes the SummarizationMapReduce object with a language model and user-defined prompts for the map and reduce steps.
    """

    def __init__(self, llm: Ollamallm,
                 map_prompt=SummarizationMapReducePrompts.map_prompt_default(),
                 combine_prompt=SummarizationMapReducePrompts.combine_prompt_default()):
        """
        Initializes the SummarizationMapReduce object with a language model and user-defined prompts for the map and reduce steps.

        Args:
            llm (Ollamallm): The language model used for summarization.
            map_prompt (str): The prompt used to guide the map step for chunk-level summarization.
            combine_prompt (str): The prompt used to guide the reduce step for combining the summaries.
        """
        Summarization.__init__(self,
            load_summarize_chain(
                llm,
                chain_type="map_reduce",
                map_prompt=map_prompt,
                combine_prompt=combine_prompt,
                combine_document_variable_name="text",
                map_reduce_document_variable_name="text"
            )
        )
        self.llm = llm