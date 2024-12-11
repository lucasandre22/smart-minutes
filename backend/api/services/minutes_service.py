from langchain.chains.summarize import load_summarize_chain
from llms.ollama.ollama_llm import Ollamallm
from action_items.action_items import ActionItems
from ner.documents.template import *
from pydantic import BaseModel, Field
from langchain_community.llms import Ollama
from langchain_ollama import ChatOllama
from ner.documents.document_entity_recognition import DocumentEntityRecognition
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from core.config import CONFIG
from api.services.service import Service
from minutes.refine import MinutesRefine

#TODO: use a centralized model


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

class Document(BaseModel):
    name: str = Field(description="nome do documento")
    citation: str = Field(description="trecho do documento que foi citado")

class MinutesService():
    llm: Ollama = Ollama(
                model=CONFIG.model,
                verbose=True,
                temperature=CONFIG.temperature,
            )
    chat_ollama = ChatOllama(
        model="llama3.1:8b-instruct-q5_1",
        temperature=0,
    )

    @staticmethod
    def generate_documents_citation_json(transcription):
        """_summary_

        Args:
            file (_type_): _description_
        """
        document_entity_recognition = DocumentEntityRecognition(MinutesService.llm)
        docs = document_entity_recognition.chunk_file_into_documents(transcription, chunk_size=2000)
        print("Length of the documents:", len(docs))
        result_json = document_entity_recognition.invoke_clean_and_get_as_list(docs)
        return result_json

    @staticmethod
    def search_for_document_structure_based_on_citation(citation):
        return Service.search_in_rag_database(citation)

    @staticmethod
    def generate_minutes(transcription_file, groups):
        document_citations = MinutesService.generate_documents_citation_json(transcription_file)
        #document_citations = [{"name": "Resolução Interna de Programa 20 Dimensões", "citation": "...essa minuta aqui ele detalha tudo tudo tudo tudo e ele tem várias menções a resolução interna de programa. 20 dimensões tá?"}, {"name": "Regulamento do PPGCA", "citation": " ...eu já vou puxar aqui para começar que é o novo regulamento do ppgca..."}, {"name": "Edital de Credenciamento do Programa de Ponta Grossa", "citation": "Esse aqui é o credenciamento do pessoal desse programa aqui de Ponta Grossa, tá?"}, {"name": "Edital de Seleção do Programa", "citation": "quando a gente fez lá a definição do edital de seleção, né? A gente colocou as vagas por uma vaga por permanente do programa"}, {"name": "Edital de Credenciamento", "citation": "a gente consegue credenciar as pessoas antes do edital de seleção começar as entrevistas"}, {"name": "Regulamento do Programa", "citation": "...no nosso regulamento anterior, né? Que ainda tá vigente por sinal a gente tinha lá o termo que era uma produção adequada, né na área de computação..."}, {"name": "Política de Alta Avaliação", "citation": "...tem campo para regulamento tem campo para para política de alta avaliação..."}, {"name": "Documento de Autoavaliação", "citation": "...elaborar um documento que deixa isso bem especificado, né? E também quando os resultados da autoavaliação vão ser apresentados..."}, {"name": "Regulamento", "citation": "...elaborar as 13 resoluções que o nosso regulamento precisa né?"}, {"name": "Regulamento", "citation": "regulamentos resoluções eu vou dividir 13 por número de integrantes e passar três ou quatro pessoas são para cada um fazer tá bom?"}]

        retriever = Service._rag_database.get_retriever()
        PROMPT = PromptTemplate(
                template="""
Você é um assistente para dar um contexto sobre o que uma citação menciona.
Use as seguintes partes do contexto recuperado para entender o que a citação está mencionando e traga um pequeno resumo sobre, baseado no contexto.
Use no máximo três frases para dar um contexto sobre a citação e mantenha a resposta concisa.

Citação: {citation}

Contexto: {context}

Resposta:
"""
        )

        rag_chain = (
            {"context": retriever | format_docs, "citation": RunnablePassthrough()}
            | PROMPT
            | MinutesService.chat_ollama
            | StrOutputParser()
        )

        print("Identified ", len(document_citations), " citations!")
        for citation in document_citations:
            

            #TODO: make a prompt to decide if the citation is pertinent or not
            #result = rag_chain_decider.invoke(citation["citation"])
            #print(result)

            result = rag_chain.invoke(citation["citation"])

            citation["context"] = result
            documents_cited = []

            docs = Service._rag_database.search_for_similar_docs(citation["citation"], 2)
            for doc in docs:
                documents_cited.append(doc.metadata["source"])
            citation["documents"] = documents_cited

        minutes_refine = MinutesRefine(MinutesService.llm, groups)
        docs = minutes_refine.chunk_file_into_documents(transcription_file)
        result = minutes_refine.invoke(docs)["output_text"]

        text_citations = ""
        i = 1
        for document in document_citations:
            text_citations += (
                "Citação" + str(i) + ": " + document["citation"] +
                "\nPossíveis documentos: " +
                document["documents"][0] + ", " + document["documents"][1] + "." +
                "\nContexto: " + document["context"] + "\n"
            )
            i += 1

        result = result + "\n------------------\nPossíveis citações a documentos durante a reunião:\n" + text_citations
        return result

def generate_minutes(transcription_file, groups):
    document_citations = MinutesService.generate_documents_citation_json(transcription_file)
    #document_citations = [{"name": "Resolução Interna de Programa 20 Dimensões", "citation": "...essa minuta aqui ele detalha tudo tudo tudo tudo e ele tem várias menções a resolução interna de programa. 20 dimensões tá?"}, {"name": "Regulamento do PPGCA", "citation": " ...eu já vou puxar aqui para começar que é o novo regulamento do ppgca..."}, {"name": "Edital de Credenciamento do Programa de Ponta Grossa", "citation": "Esse aqui é o credenciamento do pessoal desse programa aqui de Ponta Grossa, tá?"}, {"name": "Edital de Seleção do Programa", "citation": "quando a gente fez lá a definição do edital de seleção, né? A gente colocou as vagas por uma vaga por permanente do programa"}, {"name": "Edital de Credenciamento", "citation": "a gente consegue credenciar as pessoas antes do edital de seleção começar as entrevistas"}, {"name": "Regulamento do Programa", "citation": "...no nosso regulamento anterior, né? Que ainda tá vigente por sinal a gente tinha lá o termo que era uma produção adequada, né na área de computação..."}, {"name": "Política de Alta Avaliação", "citation": "...tem campo para regulamento tem campo para para política de alta avaliação..."}, {"name": "Documento de Autoavaliação", "citation": "...elaborar um documento que deixa isso bem especificado, né? E também quando os resultados da autoavaliação vão ser apresentados..."}, {"name": "Regulamento", "citation": "...elaborar as 13 resoluções que o nosso regulamento precisa né?"}, {"name": "Regulamento", "citation": "regulamentos resoluções eu vou dividir 13 por número de integrantes e passar três ou quatro pessoas são para cada um fazer tá bom?"}]

    retriever = Service._rag_database.get_retriever()
    PROMPT = PromptTemplate(
            template="""
Você é um assistente para dar um contexto sobre o que uma citação menciona.
Use as seguintes partes do contexto recuperado para entender o que a citação está mencionando e traga um pequeno resumo sobre, baseado no contexto.
Use no máximo três frases para dar um contexto sobre a citação e mantenha a resposta concisa.

Citação: {citation}

Contexto: {context}

Resposta:
"""
    )

    rag_chain = (
        {"context": retriever | format_docs, "citation": RunnablePassthrough()}
        | PROMPT
        | MinutesService.chat_ollama
        | StrOutputParser()
    )

    print("Identified ", len(document_citations), " citations!")
    for citation in document_citations:
        

        #TODO: make a prompt to decide if the citation is pertinent or not
        #result = rag_chain_decider.invoke(citation["citation"])
        #print(result)

        result = rag_chain.invoke(citation["citation"])

        citation["context"] = result
        documents_cited = []

        docs = Service._rag_database.search_for_similar_docs(citation["citation"], 2)
        for doc in docs:
            documents_cited.append(doc.metadata["source"])
        citation["documents"] = documents_cited

    minutes_refine = MinutesRefine(MinutesService.llm, groups)
    docs = minutes_refine.chunk_file_into_documents(transcription_file)
    result = minutes_refine.invoke(docs)["output_text"]

    text_citations = ""
    for document in document_citations:
        text_citations += "Citação: " + document["citation"] 
        + "\nPossíveis documentos: " 
        + str(document["documents"]) 
        + "\nContexto: " + document["context"]

    result = result + "\n------------------\nPossíveis citações a documentos:" + text_citations
    return result

if __name__ == "__main__":
    grupos = """
COLEGIADO DO PROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA - PPGCA
Daniel Fernando Pigatto (Presidente do colegiado)

COMISSÃO PERMANENTE DE SELEÇÃO DO PPGCA
Gustavo Alberto Gimenez Lugo (Presidente da comissão)
Bogdan Tomoyuki Nassu
Daniel Fernando Pigatto
Robson Ribeiro Linhares
Maria Cláudia Figueiredo Pereira Emer
Nádia Puchalski Kozievitch

COMISSÃO PERMANENTE DE REGULAMENTOS E RESOLUÇÕES DO PPGCA
João Alberto Fabro (Presidente da comissão)
Ana Cristina Barreiras Kochem Vendramin
Maria Cláudia Figueiredo Pereira Emer
Ricardo Dutra da Silva
Rita Cristina Galarraga Berardi

COMISSÃO PERMANENTE DE PLANEJAMENTO DO PPGCA
Luiz Celso Gomes Júnior (Presidente da comissão)
Bogdan Tomoyuki Nassu
Laudelino Cordeiro Bastos
Luiz Nacamura Júnior
Robson Ribeiro Linhares

COMISSÃO PERMANENTE DE AVALIAÇÃO E ACOMPANHAMENTO DO PPGCA
Adolfo Gustavo Serra Seca Neto (Presidente da comissão)
César Augusto Tacla
Juliana de Santi
João Alberto Fabro
Ricardo Dutra da Silva

COMISSÃO DE BOLSAS DO PPGCA
Adolfo Gustavo Serra Seca Neto (Presidente da comissão)
Ana Cristina Barreiras Kochem Vendramin
João Alberto Fabro

COMISSÃO DE INTERAÇÃO COM EMPRESAS E ORGANIZAÇÕES DO PPGCA
Daniel Fernando Pigatto (Presidente da comissão)
Bogdan Tomoyuki Nassu
Laudelino Cordeiro Bastos
Luiz Celso Gomes Júnior
Marco Aurélio Wehrmeister"""
    MinutesService.generate_minutes("databases/transcripts/Reunião do Colegiado do PPGCA – 2024_09_30 13_22 BRT – Recording-pt-1.csmt", grupos)