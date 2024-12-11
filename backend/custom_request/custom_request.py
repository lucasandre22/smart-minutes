from utils import chunk_into_documents
from langchain_core.documents import Document
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain

class CustomRequest():
    def __init__(self, chain):
        self.chain: BaseCombineDocumentsChain = chain
    
    def chunk_file_into_documents(self, filePath: str, chunk_size) -> list[Document]:
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        return chunk_into_documents(text, filePath, chunk_size)
    
    def invoke(self, docs: list[Document]):
        self.response = self.chain(docs)
        return self.response

    def invoke(self, text: str):
        self.response = self.chain(text)
        return self.response