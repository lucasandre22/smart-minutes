from utils import chunk
from langchain_core.documents import Document
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain

class Minutes():
    """
    A class to handle document processing for meeting minutes.

    This class provides methods for splitting large text files into smaller
    document chunks and invoking a document processing chain on those chunks.

    Attributes:
        chain (BaseCombineDocumentsChain): The chain used to combine and process documents.

    Methods:
        __init__(self, chain: BaseCombineDocumentsChain):
            Initializes the Minutes object with a document processing chain.
        
        chunk_file_into_documents(self, filePath: str, chunk_size: int = 2000) -> list[Document]:
            Chunks the text from a file into smaller documents based on the specified chunk size.
        
        invoke(self, docs: list[Document]):
            Processes the list of Document objects using the provided chain.
        
        invoke(self, text: str):
            Processes the provided text using the provided chain.
    """

    def __init__(self, chain):
        """
        Initializes the Minutes object with a document processing chain.

        Args:
            chain (BaseCombineDocumentsChain): The chain used for combining documents.
        """
        self.chain: BaseCombineDocumentsChain = chain
    
    def chunk_file_into_documents(self, filePath: str, chunk_size=2000) -> list[Document]:
        """
        Chunks the text from a file into smaller documents based on the specified chunk size.

        Args:
            filePath (str): The path to the file to be processed.
            chunk_size (int, optional): The size of each chunk. Defaults to 2000.

        Returns:
            list[Document]: A list of Document objects created from the file's content.
        """
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        chunks = chunk(text, chunk_size)
        return [Document(page_content=t) for t in chunks]
    
    def invoke(self, docs: list[Document]):
        """
        Processes the list of Document objects using the provided chain.

        Args:
            docs (list[Document]): A list of Document objects to be processed.

        Returns:
            The result of invoking the chain on the provided documents.
        """
        return self.chain(docs)

    def invoke(self, text: str):
        """
        Processes the provided text using the provided chain.

        Args:
            text (str): The text to be processed.

        Returns:
            The result of invoking the chain on the provided text.
        """
        return self.chain(text)