from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from langchain.chains import LLMChain

class Ollamallm:
    """
    Wrapper class for the Ollama LLM, providing functionality for prompt handling,
    chain initialization, and response invocation.

    Attributes:
        llm (Ollama): The instantiated LLM model.
        prompt (PromptTemplate): The prompt template used for query generation.
        chain: The processing pipeline connecting the prompt, LLM, and output parser.
    """

    def __init__(self, model: str, prompt: PromptTemplate, verbose=True, temperature=0.1, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), num_ctx=1024):
        """
        Initializes the Ollamallm instance.

        Args:
            model (str): The name of the LLM model to use.
            prompt (PromptTemplate): The template for structuring prompts.
            verbose (bool, optional): Whether to enable verbose mode. Defaults to True.
            temperature (float, optional): The temperature setting for response variability. Defaults to 0.1.
            callback_manager (CallbackManager, optional): Manages callbacks for streaming responses.
                Defaults to a standard streaming handler.
            num_ctx (int, optional): The context window size for the model. Defaults to 1024.
        """
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
        
    def set_prompt(self, prompt):
        """
        Sets a new prompt template for the model.

        Args:
            prompt (PromptTemplate): The new prompt template to use.
        """
        self.prompt = prompt
        
    def init_chain(self):
        """
        Initializes the processing chain by linking the prompt, LLM, and output parser.

        Raises:
            ValueError: If the prompt is not set before initialization.
        """
        if self.prompt is None:
            raise ValueError("The prompt is required to be initialized. Make sure to call set_prompt(prompt) before initializing the chain.")
        self.chain = self.prompt | self.llm | StrOutputParser()

    def invoke_chain(self, **kwargs):
        """
        Invokes the processing chain to generate a response based on the provided inputs.

        Args:
            **kwargs: Additional keyword arguments to be passed into the prompt.

        Returns:
            str: The generated response from the LLM.
        """
        if self.chain is None:
            self.init_chain()
        return self.chain.invoke(kwargs)

    def invoke(self, **kwargs):
        """
        Directly invokes the LLM without the processing chain.

        Args:
            **kwargs: Additional keyword arguments to be passed to the LLM.
        """
        self.llm.invoke(kwargs)

    def get_llm(self) -> Ollama:
        """
        Retrieves the underlying LLM instance.

        Returns:
            Ollama: The initialized LLM object.
        """
        return self.llm