import time
import queue
import threading
import psutil
import pandas as pd
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo

# Initialize NVML
nvmlInit()

event = threading.Event()

def start_getting_statistic_info(q: queue.Queue):
    """
    Function to get GPU average memory usage until event is set
    """
    count = 0
    gpu_used_memory_mb = 0
    gpu_free_memory_mb = 0
    cpu_usage = 0
    ram_usage = 0
    while not event.is_set():
        handle = nvmlDeviceGetHandleByIndex(0)
        info = nvmlDeviceGetMemoryInfo(handle)
        #Convert to MB
        gpu_used_memory_mb += info.used / 1024 ** 2
        gpu_free_memory_mb += info.free / 1024 ** 2
        ram_usage += psutil.virtual_memory().percent
        cpu_usage += psutil.cpu_percent(interval=1)
        count += 1

    q.put_nowait([ gpu_used_memory_mb / count, gpu_free_memory_mb / count, cpu_usage / count, ram_usage / count ])
    
def stop_statistics():
    event.set()

if __name__ == "__main__":
    thread_result = {}
    q = queue.Queue()
    x = threading.Thread(target=start_getting_statistic_info, args=(q,))
    start_time = time.time()
    x.start()
    time.sleep(1)
    stop_statistics(x)
    x.join()
    end_time = time.time()

    gpu_used_memory_mb, gpu_free_memory_mb, cpu_usage, ram_usage = q.get_nowait()
    execution_time = end_time - start_time

    benchmark_results = {
        "execution_time": execution_time,
        "gpu_used_mb": gpu_used_memory_mb,
        "gpu_free_mb": gpu_free_memory_mb,
        "cpu_usage_percent": cpu_usage,
        "ram_usage_percent": ram_usage
    }
    file = "benchmark_results.csv"
    data_frame = pd.DataFrame([benchmark_results])
    try:
        existing_data_frame = pd.read_csv(file)
        data_frame = pd.concat([existing_data_frame, data_frame], ignore_index=True)
    except FileNotFoundError:
        pass

    data_frame.to_csv(file, index=False)
    

    