from .utils import chunk
from langchain_core.documents import Document
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain

class Summarization():
    def __init__(self, chain):
        self.chain: BaseCombineDocumentsChain = chain
    
    def chunk_file_into_documents(self, filePath: str, chunk_size=3000) -> list[Document]:
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        chunks = chunk(text, chunk_size)
        # TODO: Split the input text by using a langchain method
        return [Document(page_content=t) for t in chunks]
    
    def invoke(self, docs: list[Document]):
        return self.chain(docs)

    def invoke(self, text: str):
        return self.chain(text)

    #TODO
    def generate_final_summary(self, summary):
        return summary