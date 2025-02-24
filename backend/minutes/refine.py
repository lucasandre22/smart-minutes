from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from llms.ollama.ollama_llm import Ollamallm
from .minutes import Minutes
from .template_refine import *

"""
Refine chain.

The refine documents chain constructs a response by iterating over the input documents
and progressively updating a rolling summary.
"""

class MinutesRefine(Minutes):
    """
    A summarization class that implements the refine method.

    This approach splits a document into chunks and iteratively updates 
    a summary as it processes each section in sequence.

    Attributes:
        llm (Ollamallm): The LLM instance used for summarization.
    """

    def __init__(self, llm: Ollamallm, groups):
        """
        Initializes the refinement-based summarization process.

        Args:
            llm (Ollamallm): The LLM wrapper instance for processing text.
            groups: A parameter used to generate dynamic prompts based on entity groups.

        The refinement process works by first generating an initial summary,
        then iteratively improving it as more document chunks are processed.
        """
        refine_prompt=MinutesRefinePrompts.refine_prompt(groups)
        question_prompt=MinutesRefinePrompts.organize_prompt(groups)
        Minutes.__init__(self,
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

    def generate_final_follow_up(self, follow_up):
        """
        Generates a refined follow-up summary.

        Args:
            follow_up (str): The follow-up input text to refine.

        Returns:
            str: The refined summary based on the follow-up input.
        """
        prompt = MinutesRefinePrompts.refine_prompt_default(follow_up)
        return self.llm.invoke(prompt)