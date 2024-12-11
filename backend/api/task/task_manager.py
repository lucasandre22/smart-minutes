import threading
from api.task.task import Task

class TaskManager():
    _lock = threading.Lock()
    _task = None
    _no_task = Task(name="empty", is_processing=False, state="Free", transcript="", processed_filename="")

    @classmethod
    def get_current_task(cls):
        #with cls._lock:
        if cls._task is not None:
            return cls._task
        return cls._no_task

    @classmethod
    def set_current_task(cls, task: Task):
        #with cls._lock:
        cls._task = task
            
    @classmethod
    def update_current_task(cls, details = None, state = None, is_processing = None):
       # with cls._lock:
        if(details):
            cls._task.details = details
        if(state):
            cls._task.state = state
        if(is_processing is not None):
            cls._task.is_processing = is_processing

    @classmethod
    def clear_current_task(cls):
        #with cls._lock:
        cls._task = None