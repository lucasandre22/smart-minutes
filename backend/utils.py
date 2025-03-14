import tiktoken
import math
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

ENCODING = tiktoken.get_encoding("cl100k_base")

def token_len(input: str) -> int:
    """Get token length

    Args:
        input (str): The text to get token length

    Returns:
        int: The input's token length
    """
    return len(ENCODING.encode(input))

def chunk(input: str, chunk_size=3000) -> list:
    """Generate N chunks of chunk_size of the input

    Args:
        input (str): The text to be chunked
        chunk_size (int, optional): The size of each chunk to split the text into. Default is 3000.

    Returns:
        list: List of chunks of chunk_size containing the input.
    """
    input_tokens = token_len(input)
    count = math.ceil(input_tokens / chunk_size)
    k, m = divmod(len(input), count)
    chunks = [
        input[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(count)
    ]
    return chunks

def chunk_into_documents(text, document_path, chunk_size=2000) -> list[Document]:
    chunks = chunk(text, chunk_size)
    # TODO: Split the input text by using a langchain method
    return [Document(page_content=t, metadata={"source": document_path}) for t in chunks]


def chunk_into_character_documents(content_str, document_path, chunk_size=1024) -> list[Document]:
    docs = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
        separators=[]
    )
    for chunk in text_splitter.split_text(content_str):
        docs.append(Document(page_content=chunk, metadata={"source": document_path}))
    return docs