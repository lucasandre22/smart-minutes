from langchain.prompts import PromptTemplate

class TranscriptionPrompts:
    @staticmethod
    def generate_transcription_cleaner() -> PromptTemplate:
        return PromptTemplate(
            template="""
A seguir, lhe darei uma transcrição de uma reunião que aconteceu no Programa de pós-graduação em computação aplicada de uma universidade (PPGCA).
Você tem o trabalho de limpar falas irrelevantes da transcrição e quaisquer repetições.
A sua saída deve ser EXATAMENTE como a transcrção no formato original, com a fala de cada integrante, apenas com o conteúdo não relevante removido.

Transcrição:
{transcription}

""",
            input_variables=["transcription"]
        )
        
    @staticmethod
    def generate_transcription_cleaner_test() -> PromptTemplate:
        return PromptTemplate(
            template="""
Você é um editor habilidoso e responsável pelo conteúdo editorial, e receberá uma transcrição de uma entrevista, ensaio em vídeo, podcast ou discurso. Seu trabalho é manter o máximo possível da transcrição original, fazendo apenas correções para clareza ou abreviação, gramática, pontuação e formato de acordo com este conjunto geral de regras:

Esteja ciente de que esta transcrição foi gerada automaticamente a partir de fala, então ela pode conter palavras incorretas ou mal soletradas. Faça o seu melhor para corrigir essas palavras, nunca mude a estrutura geral da transcrição; concentre-se apenas em corrigir palavras específicas, consertar a pontuação e o formato.

Antes de realizar sua tarefa, certifique-se de ler o suficiente da transcrição para que você possa inferir o contexto geral e fazer melhores julgamentos sobre as correções necessárias.

A regra mais importante é manter a transcrição original quase inalterada, palavra por palavra, e especialmente no tom. Você só pode fazer pequenas alterações editoriais na pontuação, gramática, formatação e clareza.

Você tem permissão para modificar o texto apenas se, nesse contexto, o sujeito se corrigir, então seu trabalho é limpar a frase para clareza e eliminar a repetição.

Transcrição da entrevista: {transcription}

""",
            input_variables=["transcription"]
        )