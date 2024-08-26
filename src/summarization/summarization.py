from langchain_community.llms import Ollama
from src.prompts import SUMMARIZE_CHAPTERS, SUMMARIZE_TESTING
from src.llms.ollama.ollama_llm import Ollamallm
from .template import SummarizationPrompts
from .utils import chunk
from langchain_core.documents import Document

class Summarization():
    def __init__(self, chain):
        self.chain = chain
    
    def chunk_file_into_documents(self, file, chunk_size=3000) -> list[Document]:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
        chunks = chunk(text, chunk_size)
        # TODO: Split the input text by using a langchain method
        return [Document(page_content=t) for t in chunks]
    
    def invoke(self, docs):
        return self.chain(docs)

    #TODO
    def generate_final_summary(self, summary):
        return summary

if __name__ == "__main__":
    file = ".\\documents\\ppgca\\transcript_talkers.txt"
    summarizations_by_chapters = Summarization()
    chunks = summarizations_by_chapters.chunk_file(file)

    MODEL="lucasalmeida/gemma-2-9b-it-sppo-iter3:Q4_K_M"
    prompt = SummarizationPrompts.generate_meeting_transcription_chapter_summary_test()
    llm = Ollamallm(model=MODEL, prompt=prompt)
    llm.init_chain()
    responses = []

    #Do this to generate the first summary
    print(f"Prompt has {llm.llm.get_num_tokens(prompt.format(transcription=chunks[0]))} tokens")
    previous_summary = llm.invoke_chain(transcription=chunks[0])

    #Update the prompt for the next N chapters summaries
    chapter_summary_prompt = SummarizationPrompts.generate_meeting_transcription_chapter_summary()
    llm.set_prompt(chapter_summary_prompt)
    llm.init_chain()
    print('\n' + 60 * '-' + '\n')

    for i in range(1, len(chunks)):
        current_chapter = ' '.join(str(i) for i in chunks[i])
        print(f"Prompt has {llm.llm.get_num_tokens(chapter_summary_prompt.format(transcription=chapter))} tokens")
        response = llm.invoke_chain(previous_summary=previous_summary, current_chapter=current_chapter)
        previous_summary = response
        print('\n' + 60 * '-' + '\n')
        responses.append(response)

    print(responses[-1])
