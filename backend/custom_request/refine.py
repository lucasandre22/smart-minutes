from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from llms.ollama.ollama_llm import Ollamallm
from core.config import CONFIG
from .custom_request import CustomRequest
from .template_refine import *

"""
Refine chain.

The refine documents chain constructs a response by looping over the input documents
and iteratively updating its answer.
"""

class CustomRequestRefine(CustomRequest):
    """
    A class for refining document summarization by iterating over chunks of text and generating an updated response.

    This class extends `CustomRequest` to implement a summarization chain that uses the refine method. The process involves
    splitting a document or text into chunks, and iterating over those chunks to update a rolling summary.

    Attributes:
        refine_prompt (str): The prompt used to guide the refinement of the summary.
        question_prompt (str): The prompt used to guide the organization of the action items or summary.
        llm (Ollamallm): The language model used for summarization and refinement.
    
    Methods:
        __init__(self, llm: Ollamallm, user_request: str):
            Initializes the CustomRequestRefine object with a language model and user-specific prompts for refinement and organization.
        
        generate_final_response(self):
            Placeholder method for generating a final clean response based on the refined summary.
    """

    def __init__(self, llm: Ollamallm, user_request):
        """
        Initializes the CustomRequestRefine object with a language model and user-specific prompts for refinement and organization.

        Args:
            llm (Ollamallm): The language model used for summarization and refinement.
            user_request (str): The specific request made by the user, which will influence the refinement prompts.
        """
        self.refine_prompt = CustomRequestPrompts.refine_prompt_default(user_request)
        self.question_prompt = CustomRequestPrompts.question_prompt_default(user_request)
        self.llm = llm
        CustomRequest.__init__(self,
            load_summarize_chain(
                llm,
                chain_type="refine",
                question_prompt=self.question_prompt,
                refine_prompt=self.refine_prompt, 
                document_variable_name="text", 
                initial_response_name="existing_answer"
            )
        )

    #TODO: based on the final response, generate another response that can clean the model output
    def generate_final_response(self):
        """
        Placeholder method for generating a final clean response based on the refined summary.

        This method should be implemented to improve the model's output by providing a clean, polished response.
        """
        pass
