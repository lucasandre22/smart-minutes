from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from utils import chunk_into_character_documents
from typing import List
from langchain_unstructured import UnstructuredLoader

#TODO: improve with OCR -> https://python.langchain.com/docs/how_to/document_loader_pdf/
class PdfDocumentLoader():
    def __init__(self, document_path, chunk_size, parse_doc = True):
        self.document_path = document_path
        self.loader = PyPDFLoader(document_path)
        if parse_doc:
            self.docs = PdfDocumentLoader._parse_doc_based_on_chunk_size(self.loader.load(), document_path, chunk_size)
        else:
            self.docs = self.loader.load()

    #TODO: Improve this parsing with langchain parsing: RecursiveCharacterTextSplitter
    @staticmethod
    def _parse_doc_based_on_chunk_size(docs: List[Document], document_path, chunk_size) -> List[Document]:
        page_content = ""
        for doc in docs:
            page_content = page_content + doc.page_content
        return chunk_into_character_documents(page_content, document_path, chunk_size)