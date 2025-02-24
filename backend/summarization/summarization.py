from utils import chunk_into_character_documents, chunk_into_documents
from langchain_core.documents import Document
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain

class Summarization():
    """
    A base class for performing transcript/document summarization.

    This class provides methods to chunk a document into smaller pieces, apply a summarization chain, 
    and return the summarized content.

    Attributes:
        chain (BaseCombineDocumentsChain): The summarization chain that processes the documents or text.
    
    Methods:
        __init__(self, chain: BaseCombineDocumentsChain):
            Initializes the Summarization object with a given summarization chain.
        chunk_file_into_documents(self, filePath: str, chunk_size: int) -> list[Document]:
            Reads a file, chunks its content into smaller pieces, and returns a list of Document objects.
        invoke(self, docs: list[Document]):
            Processes the provided documents using the summarization chain.
        invoke(self, text: str):
            Processes the provided text using the summarization chain.
        generate_final_summary(self, summary):
            A placeholder method for generating the final summary from the intermediate summary.
    """

    def __init__(self, chain):
        """
        Initializes the Summarization object with a given summarization chain.

        Args:
            chain (BaseCombineDocumentsChain): The summarization chain used to process documents or text.
        """
        self.chain: BaseCombineDocumentsChain = chain
    
    def chunk_file_into_documents(self, filePath: str, chunk_size) -> list[Document]:
        """
        Reads the content of a file and splits it into smaller document chunks.

        Args:
            filePath (str): The path to the file to be read.
            chunk_size (int): The maximum size for each chunk in terms of tokens or characters.

        Returns:
            list[Document]: A list of Document objects containing the chunked content.
        """
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        return chunk_into_documents(text, filePath, chunk_size)
    
    def invoke(self, docs: list[Document]):
        """
        Processes a list of documents using the summarization chain.

        Args:
            docs (list[Document]): A list of Document objects to be processed.

        Returns:
            The result of invoking the summarization chain on the documents.
        """
        return self.chain(docs)

    def invoke(self, text: str):
        """
        Processes a string of text using the summarization chain.

        Args:
            text (str): The text to be processed.

        Returns:
            The result of invoking the summarization chain on the text.
        """
        return self.chain(text)

    #TODO
    def generate_final_summary(self, summary):
        """
        Placeholder method for generating the final summary from the intermediate summary.

        This method can be overridden to further process the intermediate summary 
        and return a cleaned-up or more structured final summary.

        Args:
            summary: The intermediate summary result.

        Returns:
            The final summary (currently returns the input summary as is).
        """
        return summary