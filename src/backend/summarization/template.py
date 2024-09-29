from langchain.prompts import PromptTemplate

class SummarizationPrompts:
    @staticmethod
    def generate_meeting_transcription_summary() -> PromptTemplate:
        return PromptTemplate(
            template="""
Você é um assistente de reuniões especializado em criar resumos detalhados de reuniões do Programa de pós-graduação em computação aplicada de uma universidade (PPGCA).
Seu trabalho é resumir detalhadamente e precisamente as reuniões fornecendo uma visão clara e concisa dos principais tópicos discutidos, contendo detalhes que julgar importante.
Certifique-se de que o resumo cubra todos os aspectos relevantes, pontos-chave, decisões tomadas e ações futuras.
Além disso, siga os seguintes pontos:

Decisões e Ações: Destaque qualquer decisão tomada e as ações acordadas.
Participantes Relevantes: Mencione os participantes principais e suas contribuições específicas, se relevante.
Objetividade: Não adicione novas informações. Apenas resuma o que foi discutido de maneira clara e objetiva.
Transcrição da reunião: {transcription}

Resumo:
    """,
            input_variables=["transcription"]
        )

    @staticmethod
    def generate_meeting_transcription_chapter_summary() -> PromptTemplate:
        return PromptTemplate(
            template="""
Você é um assistente de reuniões especializado em incrementar resumos de reuniões do Programa de pós-graduação em computação aplicada de uma universidade (PPGCA).
Seu trabalho é incrementar resumos de seções da reunião fornecendo uma visão detalhada e concisa dos principais tópicos discutidos.
Ao incrementar o resumo, inclua explicitamente os pontos-chave, decisões tomadas, e ações futuras mencionadas.

Baseado no resumo anterior, atualize o resumo com os novos tópicos do capítulo atual. Mantenha clareza, objetividade, e maior quantidade de detalhes que julgar importante sem adicionar informações externas.

Atualize qualquer decisão tomada e ações acordadas, adicionando as novas informações do capítulo atual.
Mencione novos participantes e suas contribuições específicas, se houver.
Não adicione novas informações. Apenas incremente o resumo anterior com o capítulo atual de maneira clara e objetiva.
------------
Resumo do capítulo anterior: {previous_summary}
------------
Capítulo Atual: {current_chapter}
------------
Resumo atualizado:
    """,
            input_variables=["previous_summary", "current_chapter"]
        )
        
    @staticmethod
    def generate_meeting_transcription_chapter_summary_test() -> PromptTemplate:
        return PromptTemplate(
            template="""
Você é um assistente de reuniões especializado em incrementar resumos de reuniões do Programa de pós-graduação em computação aplicada de uma universidade (PPGCA).
Seu trabalho é incrementar resumos de seções da reunião, destacando tópicos principais, decisões, detalhes que julgar importantes.

Baseado no resumo anterior, atualize o resumo com os novos tópicos do capítulo atual. Não retire nenhuma informação do resumo anterior e siga o mesmo formato, apenas incremente o resumo com as informações do novo capítulo.
------------
Resumo anterior: {previous_summary}
------------
Capítulo atual: {current_chapter}
------------
Resumo atualizado:
    """,
            input_variables=["previous_summary", "current_chapter"]
        )
#Você é um assistente de reuniões especializado em criar resumos precisos e verificáveis.
#Seu trabalho é resumir as reuniões fornecendo uma visão clara e concisa dos principais tópicos discutidos.
#Ao criar o resumo, inclua explicitamente os pontos-chave, decisões tomadas, e ações futuras mencionadas.
#Certifique-se de que o resumo cubra todos os aspectos relevantes que poderiam ser confirmados ou negados por perguntas diretas.
#
#Resumo Estruturado: Identifique e resuma os tópicos principais abordados durante a reunião.
#Decisões e Ações: Destaque qualquer decisão tomada e as ações acordadas.
#Participantes Relevantes: Mencione os participantes principais e suas contribuições específicas, se relevante.
#Objetividade: Não adicione novas informações. Apenas resuma o que foi discutido de maneira clara e objetiva.