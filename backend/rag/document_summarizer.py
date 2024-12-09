import json
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from .template_document_summarizer import DocumentSummarizerPrompts
from .document_loader import PdfDocumentLoader
from .template import *
from summarization.refine import SummarizationRefine

from .database.jsonl_rag_database import JsonlRagDatabase

class DocumentSummarizer():
    def __init__(self, loader: PdfDocumentLoader, model="lucasalmeida/gemma-2-9b-it-sppo-iter3:Q4_K_M",
                 refine_prompt=DocumentSummarizerPrompts.refine_prompt_default(), question_prompt=DocumentSummarizerPrompts.organize_prompt_default()):
        self.llm = Ollama(
            model=model,
            verbose=True,
            temperature=0,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )
        self.refine_prompt = refine_prompt
        self.question_prompt = question_prompt
        self.chain = SummarizationRefine(self.llm, self.refine_prompt, self.question_prompt)
        self.loader = loader
    
    def generate(self):
        result = self.chain.invoke(document_loader.docs)["output_text"]
        #TODO: use langchain to map output to a pydantic model
        return DocumentSummarizer._find_json_in_llm_response(result)

    @staticmethod
    def _find_json_in_llm_response(text):
        """From a text, which can be a LLM output, find and get the first json structure if any

        Args:
            text (str): text to find the json structure on

        Raises:
            json.JSONDecodeError: if error when parsing json
            json.JSONDecodeError: if no json is capable to be parse

        Returns:
            str: the json structure
        """
        depth = 0
        json_start = None

        for i, char in enumerate(text):
            if char == '{':
                if depth == 0:
                    json_start = i
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and json_start is not None:
                    possivel_json = text[json_start:i+1]
                    try:
                        return json.loads(possivel_json)
                    except json.JSONDecodeError:
                        raise json.JSONDecodeError(msg="Error when trying to parse JSON structure from LLM response")
        raise json.JSONDecodeError(msg="Unable to find JSON structure from LLM response")

if __name__ == "__main__":
    document_loader = PdfDocumentLoader("documents/rag/regulamento_ppgca.pdf")
    refiner = DocumentSummarizer(document_loader)
    json_result = refiner.generate()
    print(json_result)
    rag_db = JsonlRagDatabase("docs_database", "testing.jsonl")
    rag_db.load_db()
    rag_db.update_db(json_result)
    docs = rag_db.search_for_similar_docs("testing")
    print(docs)