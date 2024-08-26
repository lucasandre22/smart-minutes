from langchain.prompts import PromptTemplate

class SummarizationMapReducePrompts:

    @staticmethod
    def map_prompt_default():
        return PromptTemplate.from_template(
        """
Escreva um resumo conciso do seguinte texto:

"{text}"

RESUMO CONCISO:
""")
        
    @staticmethod
    def combine_prompt_default():
        return PromptTemplate.from_template(
        """
Escreva um resumo conciso do seguinte texto:

"{text}"

RESUMO CONCISO:
""")