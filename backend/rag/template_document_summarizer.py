from langchain.prompts import PromptTemplate

class DocumentSummarizerPrompts:

    @staticmethod
    def refine_prompt_default() -> str:
        return PromptTemplate.from_template("""
Você é um assistente de IA especializado em processamento de documentos. 
Para cada documento que for fornecido, preciso que você crie um resumo de 100 palavras,
identifique o título apropriado e que representem bem o conteúdo do documento.
A estrutura final deve estar no formato JSON e estritamente no formato JSON. Retorne apenas o JSON. Não insira quaisquer outros caracteres fora o JSON.
------
Exemplo de saída:
{{
    "summary":"insira o resumo aqui",
    "title":"insira o título aqui",
}}
-----
Fornecemos uma estrutura JSON até um certo ponto: {existing_answer}

Temos a oportunidade de refinar o resumo (apenas se necessário) com um contexto adicional abaixo.
------------
{text}
------------
Dado o novo contexto, refine o resumo da estrutura json.
Se o contexto não for útil, retorne a estrutura original.
""")

    @staticmethod
    def organize_prompt_default() -> str:
        return PromptTemplate.from_template("""
Escreva um resumo conciso de 100 palavras do seguinte texto:


"{text}"


RESUMO CONCISO:
""")