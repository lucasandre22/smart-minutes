from langchain.prompts import PromptTemplate

class MinutesRefinePrompts:

    @staticmethod
    def refine_prompt_default() -> str:
        return PromptTemplate.from_template(
        """
Sua tarefa é produzir uma ata de reunião final.
Fornecemos a ata de reunião existente até um certo ponto: {existing_answer}
Temos a oportunidade de refinar a ata de reunião existente (apenas se necessário) com um contexto adicional abaixo.
------------
{text}
------------
Dado o novo contexto, refine a ata de reunião original.
Se o contexto não for útil, retorne a ata de reunião original.
""")

    @staticmethod
    def organize_prompt_default() -> str:
        return PromptTemplate.from_template(
        """
Organize a seguinte ata de reunião e remova instruções que não pertencem a ata de reunião:


"{text}"


ATA DE REUNIÃO CONCISA:
""")

    @staticmethod
    def refine_prompt(groups) -> str:
        return PromptTemplate.from_template(
        """
Sua tarefa é produzir uma ata de reunião final que contenha informações claras, objetivas e completas sobre o que foi discutido e decidido durante o encontro, assim como tarefas atribuídas.
Nesta reunião, estão presentes certos grupos ou pessoas:
-----------""" + groups + """
-----------
Identifique possíveis tarefas destinadas a certos grupos ou pessoas e inclua na ata de reunião.
Fornecemos a ata de reunião existente até um certo ponto: {existing_answer}
Temos a oportunidade de refinar a ata de reunião existente (apenas se necessário) com um contexto adicional abaixo.
------------
{text}
------------
Dado o novo contexto, refine a ata de reunião original.
Se o contexto não for útil, retorne a ata de reunião original.
""")

    @staticmethod
    def organize_prompt(groups) -> str:
        return PromptTemplate.from_template(
        """
Sua tarefa é produzir uma ata de reunião que contenha informações claras, objetivas e completas sobre o que foi discutido e decidido durante o encontro, assim como tarefas atribuídas.
Nesta reunião, estão presentes certos grupos ou pessoas:
-----------""" + groups + """
-----------
Identifique possíveis tarefas destinadas a certos grupos ou pessoas e inclua na ata de reunião.
Texto para gerar a ata de reunião:

"{text}"


ATA DE REUNIÃO CONCISA:
""")

    @staticmethod
    def generate_final_follow_up() -> str:
        return PromptTemplate.from_template(
        """
Organize a seguinte ata de reunião:


"{text}"


ATA DE REUNIÃO CONCISA:
""")