from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from src.prompts import SUMMARIZE_CHAPTERS, SUMMARIZE_TESTING
import time

#MODEL="phi3:14b-medium-128k-instruct-q5_1"
MODEL="llama3:8b-instruct-q8_0"

llm = Ollama(
    model=MODEL,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

def split_text_by_words(file):
    """ Split the text contained in file into a list of words

    Args:
        file (_type_): file path

    Returns:
        _type_: _description_
    """
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    words = text.split()
    split_text = []
    
    words_interval = 5000

    for i in range(0, len(words), words_interval):
        split_text.append(words[i:i+words_interval])

    return split_text

file = ".\\documents\\ppgca\\transcript_talkers.txt"
splitted_text = split_text_by_words(file)

chain_chapters = LLMChain(llm=llm, prompt=SUMMARIZE_CHAPTERS)
responses = []

for i in range(0, len(splitted_text)):
    text = ' '.join(str(i) for i in splitted_text[i])
    chain_chapters = LLMChain(llm=llm, prompt=SUMMARIZE_CHAPTERS)
    response = chain_chapters.run(chapter=text)
    print("\n----------------------------------------------------------------------------------------------------------\n")
    responses.append(response)

summarization_chapters = ""
i = 1
for summary in responses:
    summarization_chapters += "Resumo " + str(i) + ": " + summary
    i += 1

chain_all = LLMChain(llm=llm, prompt=SUMMARIZE_TESTING)

print("\nSending all summaries to the model...")
before = time.time()
final_response = chain_all.run(summaries=summarization_chapters)

print("\nTotal time spent by the model: ", time.time() - before)
