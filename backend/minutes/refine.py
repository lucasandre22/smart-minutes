from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from backend.llms.ollama.ollama_llm import Ollamallm
from .minutes import FollowUp
from .template_refine import *

"""Refine chain.

The refine documents chain constructs a response by looping over the input documents
and iteratively updating its answer.
"""

class FollowUpRefine(FollowUp):
    """Summarization that uses refine method:
    Splits up a document or text into chunks, update a rolling summary be iterating over the documents in a sequence.
    """
    def __init__(self, llm: Ollamallm,
                 refine_prompt=FollowUpRefinePrompts.refine_prompt_default(),
                 question_prompt=FollowUpRefinePrompts.question_prompt_default()):
        FollowUp.__init__(self,
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
        prompt = FollowUpRefinePrompts.refine_prompt_default(follow_up)
        return self.llm.invoke(prompt)

if __name__ == "__main__":
    MODEL="lucasalmeida/gemma-2-9b-it-sppo-iter3:Q4_K_M"
    LLM = Ollama(
        model=MODEL,
        verbose=True,
        temperature=0,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        #top_k=5
    )
    file = ".\\documents\\ppgca\\ppgca_.txt"

    summarization_refine = FollowUpRefine(LLM)
    docs = summarization_refine.chunk_file_into_documents(file)

    result = summarization_refine.invoke(docs)

    print("Resultado:")
    print(result["output_text"])