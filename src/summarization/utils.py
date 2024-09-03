import tiktoken
import math

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