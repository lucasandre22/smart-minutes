from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from llms.ollama.ollama_llm import Ollamallm
from core.config import CONFIG
from .summarization import Summarization
from .template_refine import *

"""
Refine chain.

The refine documents chain constructs a response by looping over the input documents
and iteratively updating its answer.
"""

class SummarizationRefine(Summarization):
    """
    A class for performing summarization using the refine method.

    This class extends `Summarization` to implement a summarization chain that splits a document or text into chunks,
    iteratively updates a rolling summary by processing each chunk in sequence.

    Attributes:
        llm (Ollamallm): The language model used for summarization.
    
    Methods:
        __init__(self, llm: Ollamallm, refine_prompt: str, question_prompt: str):
            Initializes the SummarizationRefine object with a language model and user-defined prompts for the refine and question steps.
        organize_summary(self):
            A placeholder method for organizing the summary in a timeline.
    """

    def __init__(self, llm: Ollamallm,
                 refine_prompt=SummarizationRefinePrompts.refine_prompt_default(),
                 question_prompt=SummarizationRefinePrompts.question_prompt_default()):
        """
        Initializes the SummarizationRefine object with a language model and user-defined prompts for the refine and question steps.

        Args:
            llm (Ollamallm): The language model used for summarization.
            refine_prompt (str): The prompt used to guide the refine step for iteratively updating the summary.
            question_prompt (str): The prompt used to guide the question step for refining the summary.
        """
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
        """
        Organizes the summary into a timeline.

        This is a placeholder method, which is intended to later organize the summary into a structured timeline format.
        """
        pass
