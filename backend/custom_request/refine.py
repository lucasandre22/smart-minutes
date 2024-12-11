from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from llms.ollama.ollama_llm import Ollamallm
from core.config import CONFIG
from .custom_request import CustomRequest
from .template_refine import *

"""Refine chain.

The refine documents chain constructs a response by looping over the input documents
and iteratively updating its answer.
"""

class CustomRequestRefine(CustomRequest):
    """Summarization that uses refine method:
    Splits up a document or text into chunks, update a rolling summary be iterating over the documents in a sequence.
    """
    def __init__(self, llm: Ollamallm, user_request):
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

    #TODO: make the result better by improving prompts
    summarization_refine = CustomRequestRefine(LLM, "Eu quero que sejam extraídos os momentos engraçados da reunião")
    docs = summarization_refine.chunk_file_into_documents(file)

    result = summarization_refine.invoke(docs)

    print(result["output_text"])