import subprocess
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from src.summarization.refine import SummarizationRefine

from src.evalluation.summarization.meeting_summarization_metric import LLMTestCase, MeetingSummarizationMetric
from src.evalluation.ollama_eval_model import OllamaEvalModel
from src.evalluation.summarization.template import *
import requests
from pathlib import Path


class Service():
    def __init__(self):
        self.ollama_api = "http://localhost:11434"
        self.transcriptions_directory = "./transcriptions"
        self.documents_directory = "./documents"
        pass
    
    def get_models(self):
        response = requests.get(f"{self.ollama_api}/api/tags")

        if response.status_code == 200:
            models_array = []
            for model in response.json()["models"]:
                models_array.append(model["name"])
            return models_array
        else:
            print(f"Failed to retrieve tags: {response.status_code}")
            return []
    
    def list_transcription_files(self):
        return self.list_files(self.transcriptions_directory)
    
    def list_document_files(self):
        return self.list_files(self.documents_directory)
        
    def list_files(self, directory):
        path = Path(directory)
        return [str(file) for file in path.rglob('*') if file.is_file()]
        
    def send(self, configuration):
        model=configuration["modelSelected"]
        temperature=configuration["modelConfiguration"]["temperature"]
        print(model, temperature)
        LLM = Ollama(
            model=model,
            verbose=True,
            temperature=0,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            num_ctx=8192
        )
        file = ".\\documents\\ppgca\\transcript_talkers.txt"
        print("Starting...")

        summarization_refine = SummarizationRefine(LLM)
        docs = summarization_refine.chunk_file_into_documents(file)

        result = summarization_refine.invoke(docs)
        result = summarization_refine.generate_final_summary(result)

        #result = 'O texto discute pontos para aprimorar o programa de mestrado, baseando-se em uma autoavaliação interna e nas últimas avaliações da CAPES. O coordenador destaca a necessidade de:\n\n* **Diminuir o tempo médio de conclusão do mestrado**, incentivando a gestão eficiente dos alunos.\n* **Aumentar o número de alunos formados por docente**, uma métrica importante para a CAPES.\n* **Incentivar a produção técnica**, buscando publicações e projetos, com foco em auxiliar os egressos a reportarem suas produções.\n* **Promover a integração entre alunos da mesma linha de pesquisa**, através de eventos e seminários.\n* **Garantir o engajamento docente**, buscando bolsas, financiamentos e atuando com empresas.\n* **Fortalecer as ações de divulgação do programa**, incentivando a participação docente em eventos e divulgação de atividades.\n* **Aumentar a submissão de artigos com participação docente**, buscando maior impacto científico.\n* **Melhorar a qualidade do relatório das atividades para a CAPES**, com informações precisas e completas.\n\nPara alcançar esses objetivos, o coordenador propõe uma coleta de respostas individual dos docentes sobre a autoavaliação, seguida de uma devolutiva em grupo para alinhar visões e ações.  \n\nAlém disso, o texto destaca:\n\n* **A necessidade de aprimorar a comunicação e o acesso à informação**, com a reestruturação do site do programa e a criação de um guia para o lançamento de produção técnica no Lattes.\n* **A importância de fortalecer a participação em editais**, como o Move América da CAPES, o mestrado acadêmico CNPQ e o edital de extensão da UTFPR.\n* **A criação de eventos de divulgação do programa**, liderados pelas comissões de seleção e interação com empresas, para o segundo semestre.\n* **A elaboração de um novo regulamento para o programa**, com 66 artigos, que visa resolver questões e aprimorar a gestão do mestrado.\n\n**Novas discussões surgem a partir da proposta de incluir um novo tipo de colaborador: o "Pesquisador Associado".**  A ideia é permitir que profissionais com mestrado, atuantes em empresas, se envolvam com o programa, participando de pesquisas, publicando artigos e eventualmente ingressando no corpo docente.  O debate aborda:\n\n* **Critérios para seleção e validade do programa de trabalho do Pesquisador Associado.**\n* **Possibilidade de concessão de créditos para alunos que participam do programa "Papos" (estudantes de graduação que se envolvem com a pós-graduação).**\n* **Vinculação do tema do TCC da graduação com a linha de pesquisa do mestrado, potencialmente gerando créditos para o aluno.**\n\n**Adicionalmente, surge a discussão sobre a exigência de produção técnica como requisito para conclusão do mestrado, com foco em criar um sistema para registrar e avaliar essas produções, como relatórios técnicos, artigos e código fonte, em repositórios específicos (GitHub, Google Sites, etc.).**\n\n**Uma nova proposta surge para flexibilizar a formatação da dissertação, permitindo a submissão de um artigo científico em formato de revista, como forma de defesa, em vez da tradicional dissertação.** Essa mudança visa simplificar o processo, alinha-lo com práticas comuns na pesquisa e potencializar a publicação dos trabalhos.\n\n**No contexto adicional, destaca-se a intenção de:**\n\n* **Criar um evento presencial com foco em divulgação do programa, incluindo uma mesa redonda com empresas e relato de experiências de interação com indústrias.**\n* **Organizar uma "jornada de formação" para futuros alunos, com foco em auxiliar na elaboração de pré-propostas e familiarização com o processo de pesquisa.**\n* **Realizar ciclos de lives com atores da indústria, ex-alunos e professores, para ampliar a visibilidade do programa e promover networking.**\n* **Convidar o professor Tigrão, assessor da CAPES para mestrados profissionais, para palestra e reunião de trabalho, visando fortalecer a relação com a CAPES e obter feedback sobre o programa.**\n\nEm suma, o objetivo é fortalecer o programa, aumentar sua visibilidade e garantir sua renovação pela CAPES, com foco na qualidade da formação, na produção científica e na integração com o mercado de trabalho. A inclusão do "Pesquisador Associado" busca ampliar o alcance e a relevância do programa, conectando-o com profissionais da indústria e potencializando a pesquisa aplicada. A implementação de um sistema para registrar e avaliar a produção técnica visa valorizar esse tipo de trabalho e contribuir para o desenvolvimento profissional dos alunos. A discussão sobre a formatação da dissertação busca flexibilizar as exigências e reconhecer diferentes tipos de produção acadêmica.\n\n\n'

        input_list: list = [ doc.page_content for doc in docs]
        actual_output = result["output_text"]

        test_case = LLMTestCase(input=input_list, actual_output=actual_output)
        model = OllamaEvalModel()

        metric = MeetingSummarizationMetric(
            threshold=0.5,
            model=model,
            verbose_mode=True,
            async_mode=False,
            #n represents the number of questions, it can be by chapters or not
            n=1
        )

        score: float = metric.measure(test_case)
        reason: str = metric.reason
        logs = metric.verbose_logs

        print(score)
        print(metric.total_time_to_measure)
        print(reason)
