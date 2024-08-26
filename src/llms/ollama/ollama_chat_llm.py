from langchain_community.chat_models import ChatOllama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class OllamaChatllm:
    def __init__(self, model, verbose=True, temperature=0):
        self.llm = ChatOllama(
            model,
            verbose,
            temperature,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )
        
    def __init__(self, **kwargs):
        self.llm = ChatOllama(kwargs)