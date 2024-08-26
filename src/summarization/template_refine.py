from langchain.prompts import PromptTemplate

class SummarizationRefinePrompts:

    @staticmethod
    def refine_prompt_default():
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
    def question_prompt_default():
        return PromptTemplate.from_template(
        """
Escreva um resumo conciso do seguinte texto:


"{text}"


RESUMO CONCISO:
""")
    
    @staticmethod
    def refine_prompt_transcript():
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

# refine_prompt = PromptTemplate.from_template(
#     """
#     Your job is to produce a final summary.
#     We have provided an existing summary up to a certain point: {existing_answer}
#     We have the opportunity to refine the existing summary (only if needed) with 
#     some more context below.
#     ------------
#     {text}
#     ------------
#     Given the new context, refine the original summary.
#     If the context isn't useful, return the original summary.
#     """ 
# )
 
# question_prompt = PromptTemplate.from_template(
#     """
#     Write a concise summary of the following:
    
    
#     "{text}"
    
    
#     CONCISE SUMMARY:
#     """
# )