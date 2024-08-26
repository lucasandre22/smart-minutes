from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from src.prompts import SUMMARIZE_CHAPTERS, SUMMARIZE_TESTING
from src.llms.ollama.ollama_llm import Ollamallm
from .template import TranscriptionPrompts

class TranscriptionCleaner():
    def __init__(self, model="llama3:latest", prompt=TranscriptionPrompts.generate_transcription_cleaner(), words_interval=1000):
        self.prompt = prompt
        self.llm = Ollamallm(model=model, prompt=prompt, temperature=0)
        self.splitted_transcription = None
        self.words_interval = words_interval
        
    def split_transcription(self, transcription):
        """ Split the text contained in transcription into a list of words

        Args:
            file (_type_): file path

        Returns:
            _type_: _description_
        """

        words = transcription.split()
        splitted_transcription = []

        for i in range(0, len(words), self.words_interval):
            splitted_transcription.append(words[i:i+self.words_interval])
            
        self.splitted_transcription = splitted_transcription

        return splitted_transcription
        
    def clean_transcription(self):
        if self.splitted_transcription is None:
            raise ValueError("Make sure to call split_transcription before cleaning it")

        split_text_cleaned = []
        
        for i in range(0, len(self.splitted_transcription)):
            text = ' '.join(str(i) for i in self.splitted_transcription[i])
            cleaned_text = self.llm.invoke_chain(transcription=text)
            split_text_cleaned.append(cleaned_text)

        return split_text_cleaned

if __name__ == "__main__":
    cleaner = TranscriptionCleaner(prompt=TranscriptionPrompts.generate_transcription_cleaner(), words_interval=500)
    file = ".\\documents\\ppgca\\transcript_talkers.txt"
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    cleaner.split_transcription(text)
    split_text_cleaned = cleaner.clean_transcription()

    print(split_text_cleaned)