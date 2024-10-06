from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain import hub
from src.prompts import SUMMARIZE_CHAPTERS
from src.benchmarks.hardware_statistics import *
import time
import queue
import threading
import pandas as pd

MODEL="aya:8b-23-q8_0"

llm = Ollama(
    model=MODEL,
    temperature=0,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

content = ""
with open("D:\\Git\\tcc\\documents\\benchmark.txt", 'r', encoding='utf-8') as f:
    content = f.read()

chain = LLMChain(llm=llm, prompt=SUMMARIZE_CHAPTERS)

q = queue.Queue()
x = threading.Thread(target=start_getting_statistic_info, args=(q,))
start_time = time.time()
x.start()

print("\nRunning the model...")
result = chain.run(chapter=content)

stop_statistics()
x.join()
end_time = time.time()

benchmark_array = q.get_nowait()
#gpu_used_memory_mb, gpu_free_memory_mb, cpu_usage, ram_usage = q.get_nowait()
execution_time = end_time - start_time

benchmark_results = {
    "execution_time_in_seconds": execution_time,
    "gpu_used_mb": benchmark_array[0],
    "gpu_free_mb": benchmark_array[1],
    "cpu_usage_percent": benchmark_array[2],
    "ram_usage_percent": benchmark_array[3],
    "model_name": MODEL
}
file = "benchmark_results.csv"
data_frame = pd.DataFrame([benchmark_results])
try:
    existing_data_frame = pd.read_csv(file)
    data_frame = pd.concat([existing_data_frame, data_frame], ignore_index=True)
except FileNotFoundError:
    pass

data_frame.to_csv(file, index=False)
