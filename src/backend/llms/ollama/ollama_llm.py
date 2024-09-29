from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from langchain.chains import LLMChain

class Ollamallm:
    def __init__(self, model: str, prompt: PromptTemplate, verbose=True, temperature=0.1, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), num_ctx=1024):
        self.llm = Ollama(
            model=model,
            verbose=verbose,
            temperature=temperature,
            num_ctx=num_ctx, 
            callback_manager=callback_manager, #This allow to stream the responses, e.g. define a method that runs once each token is generate
            #top_k=5
        )
        self.prompt = prompt
        self.chain = None
        
        #num_ctx=131072 #llama3.1 ctx! The idea is that users most likely want to balance model size and context size.
        #temperature
        #top_k
        #top_p
        #num_ctx: Optional[int] = None: Sets the size of the context window used to generate the next token. (Default: 2048)
        #num_predict: Maximum number of tokens to predict when generating text. (Default: 128, -1 = infinite generation, -2 = fill context)
        #tfs_z: tail free sampling:
        
    def set_prompt(self, prompt):
        self.prompt = prompt
        
    def init_chain(self):
        if self.prompt is None:
            raise ValueError("The prompt is required to be initialized. Make sure to call set_prompt(prompt) before initializing the chain.")
        self.chain = self.prompt | self.llm | StrOutputParser()

    def invoke_chain(self, **kwargs):
        if self.chain is None:
            self.init_chain()
        return self.chain.run(kwargs)
        #return self.chain.invoke(kwargs)

    def invoke(self, **kwargs):
        self.llm.invoke(kwargs)

    def get_llm(self) -> Ollama:
        return self.llm