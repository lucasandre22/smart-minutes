from langchain.prompts import PromptTemplate

class ActionItemsRefinePrompts:

    @staticmethod
    def refine_prompt_default() -> str:
        return PromptTemplate.from_template(
        """
Sua tarefa é refinar uma ata de actions items com base na transcrição de uma reunião.
A reunião inclui várias comissões de pessoas, cada uma com um nome e tarefas atribuídas.
Você já recebeu a ata dos action items até um certo ponto: {existing_answer}
Temos a oportunidade de refinar a ata de action items (apenas se necessário) com um contexto adicional abaixo:
------------
{text}
------------
Dado o novo contexto, refine a ata de actions items APENAS se o contexto reunir informações sobre as comissões e suas tarefas.
Atualize ou adicione tarefas apenas para as comissões mencionadas no novo contexto.
Se o contexto não mencionar comissões ou tarefas adicionais, retorne ata de action items original sem modificações.
""")
        
    @staticmethod
    def refine_prompt_default_original() -> str:
        return PromptTemplate.from_template(
        """
Sua tarefa é refinar uma ata de actions items com base na transcrição de uma reunião.

Nesta reunião, estão presentes várias comissões de pessoas e cada comissão possui um nome, bem como tarefas a serem feitas para cada uma delas.
Em determinado momento da transcrição, foram discutidos as tarefas a serem feitas por cada comissão.
Fornecemos a ata de de actions items até um certo ponto: {existing_answer}
Temos a oportunidade de refinar a ata action items (apenas se necessário) com um contexto adicional abaixo:
------------
{text}
------------
Dado o novo contexto, refine a ata de actions items APENAS se o contexto reunir informações sobre as comissões presentes na reunião.
Atualize ou adicione tarefas apenas para as comissões mencionadas no novo contexto.
Se o contexto não mencionar comissões ou tarefas adicionais, retorne ata original sem modificações.
""")

    @staticmethod
    def organize_prompt_default() -> str:
        return PromptTemplate.from_template(
        """
Sua tarefa é gerar uma ata de actions items com base na transcrição de uma reunião para cada comissão.
Nesta reunião, estão presentes várias comissões de pessoas e cada comissão possui um nome, bem como tarefas a serem feitas para cada uma delas.
Em determinado momento da transcrição, foram discutidos as tarefas a serem feitas por cada comissão.

gere uma ata de actions items APENAS se o contexto reunir informações sobre as comissões presentes na reunião.
Adicione tarefas apenas para as comissões mencionadas no novo contexto.
Se o contexto não mencionar comissões ou tarefas adicionais, retorne uma string vazia.

"{text}"


ATA DE ACTION ITEMS POR COMISSÃO:
""")