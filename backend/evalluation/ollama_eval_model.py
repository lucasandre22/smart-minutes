from langchain_community.llms import Ollama
from langchain_core.language_models.llms import BaseLLM
from deepeval.models import DeepEvalBaseLLM

class OllamaEvalModel(DeepEvalBaseLLM):
    def __init__(self, model="lucasalmeida/gemma-2-9b-it-sppo-iter3:Q4_K_M"):
        self.model = Ollama(
            model=model,
            verbose=True,
            temperature=0,
            #callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )

    def load_model(self)-> BaseLLM:
        return self.model

    def generate(self, prompt: str) -> str:
        model = self.load_model()
        return model.invoke(prompt)

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return "OllamaEvalModel"