from langchain.prompts import PromptTemplate

class SummarizationRefinePrompts:

    @staticmethod
    def refine_prompt_default() -> str:
        return PromptTemplate.from_template(
        """
Sua tarefa é produzir um resumo final.
Fornecemos um resumo existente até um certo ponto: {existing_answer}
Temos a oportunidade de refinar o resumo existente (apenas se necessário) com um contexto adicional abaixo.
------------
{text}
------------
Dado o novo contexto, refine o resumo original.
Se o contexto não for útil, retorne o resumo original.
""")

    @staticmethod
    def question_prompt_default() -> str:
        return PromptTemplate.from_template(
        """
Escreva um resumo conciso do seguinte texto:


"{text}"


RESUMO CONCISO:
""")
    
    @staticmethod
    def refine_prompt_transcript() -> str:
        return PromptTemplate.from_template(
        """
Sua tarefa é produzir um resumo final de uma reunião.
Além disso, mencione os participantes principais e suas contribuições específicas, se relevante.
Fornecemos um resumo existente até um certo ponto: {existing_answer}
Temos a oportunidade de refinar o resumo existente (apenas se necessário) com um contexto adicional abaixo.
------------
{text}
------------
Dado o novo contexto, refine o resumo original.
Se o contexto não for útil, retorne o resumo original.
""")