from langchain.prompts import PromptTemplate

class CustomRequestPrompts:

    @staticmethod
    def refine_prompt_default(user_request) -> str:
        return PromptTemplate.from_template(
        """
Sua tarefa é pesquisar e fornecer, baseado no texto, a seguinte requisição de um usuário:
-----------""" + user_request + """
-----------
Fornecemos o conteúdo anteriormente gerado até um certo ponto: {existing_answer}
Temos a oportunidade de refinar o conteúdo gerado (apenas se necessário) com um contexto adicional abaixo.
------------
{text}
------------
Dado o novo contexto, refine a requisição feita pelo usuário.
Se o novo contexto não for útil, retorne o conteúdo original fornecido.
""")

    @staticmethod
    def question_prompt_default(user_request) -> str:
        return PromptTemplate.from_template(
        """
Dado uma transcrição de uma reunião, sua tarefa é extrair o que o usuário pediu.
O usuário pediu:
-----------""" + user_request + """
-----------

Transcrição:
-----------
"{text}"
-----------

INFORMAÇÃO RELEVANTE:
""")