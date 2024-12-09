import requests
import os
import json
import asyncio
import time
from datetime import datetime
from fastapi import UploadFile
from fastapi.responses import FileResponse
from evalluation.summarization.template import *
from pathlib import Path
from core.config import *
from api.task.task_manager import TaskManager
from api.task.task import Task
from api.services.pdf_service import create_pdf

OLLAMA_API_ADDRESS = os.getenv("OLLAMA_API_ADDRESS")

class Service():
    _task_manager: TaskManager = TaskManager()

    @staticmethod
    async def event_generator():
        current_data = Service._task_manager.get_current_task()
        old_data = None
        while True:
            # Create a JSON event payload
            if old_data == None or old_data != current_data:
                print("Sending new event")
                old_data = current_data
                event_data = {
                    "event": "update",
                    "task": current_data.toJSON(),
                }
                #Send the JSON data
                yield f"data: {json.dumps(event_data)}\n\n"
            current_data = Service._task_manager.get_current_task()
            await asyncio.sleep(1)
            
    @staticmethod
    def clear_current_task():
        Service._task_manager.clear_current_task()

    @staticmethod
    def get_available_models():
        response = requests.get(f"{OLLAMA_API_ADDRESS}/api/tags")

        if response.status_code == 200:
            models_array = []
            for model in response.json()["models"]:
                models_array.append(model["name"])
            return models_array
        else:
            print(f"Failed to retrieve tags: {response.status_code}")
            return []

    @staticmethod
    def list_transcriptions():
        return Service.list_files(os.getenv("TRANSCRIPTS_PATH"))

    @staticmethod
    def list_documents():
        return Service.list_files(os.getenv("DOCUMENTS_PATH"))
    
    @staticmethod
    def list_processed_files():
        return Service.list_files(os.getenv("PROCESSED_FILES_PATH"))

    @staticmethod
    def list_files(directory):
        path = Path(directory)
        return [str(os.path.basename(file)) for file in path.rglob('*') if file.is_file()]
    
    @staticmethod
    async def upload_file(source_file: UploadFile, destination_path: str):
        file_path = os.path.join(destination_path, source_file.filename)
        with open(file_path, "wb") as f:
            content = await source_file.read()
            f.write(content)
        return Service.list_files(os.getenv("DOCUMENTS_PATH"))

    async def upload_transcript_file(source_file: UploadFile, destination_path: str):
        await Service.upload_file(source_file, destination_path)
        pass

    @staticmethod
    def download_file(file_path: str, file_name: str):
        return FileResponse(path=file_path, filename=file_name, media_type="application/octet-stream")

    @staticmethod
    def remove_file(file_path: UploadFile):
        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def send(configuration):
        pass
    
    @staticmethod
    def get_current_settings():
        temperature = CONFIG.temperature
        model = CONFIG.model
        top_p = CONFIG.top_p
        debug_traces = CONFIG.debug_traces
        return { "availableModels": Service.get_available_models(), "selectedModel": model, "temperature": temperature, "top_p": top_p, "debug_traces": debug_traces }

    @staticmethod
    def set_current_settings(json):
        CONFIG.temperature = json["temperature"]
        CONFIG.model = json["selectedModel"]
        CONFIG.top_p = json["topP"]
        CONFIG.debug_traces = json["debugTraces"]

    @staticmethod
    def download_model(json):
        #TODO
        model = json["model"]

    @staticmethod
    def generate_summary(transcript, chunk_size, summarization_language, enable_evalluation_system):
        #TODO
        processed_filename = "summarization.pdf"
        summarization_task = Task(name="Summarization", is_processing=True, state="Processing", transcript=transcript, processed_filename=processed_filename)
        Service._task_manager.set_current_task(summarization_task)

        #Mock generation time
        time.sleep(10)

        create_pdf(content="example pdf", output_filename=os.path.join(os.environ["PROCESSED_FILES_PATH"], processed_filename))

        summarization_task = Task(name="Summarization", is_processing=False, state="Ready", transcript=transcript, processed_filename=processed_filename)
        Service._task_manager.set_current_task(summarization_task)
    
    @staticmethod
    def generate_custom_request(transcript, chunk_size, output_language, user_request):
        #TODO
        processed_filename = "custom.pdf"
        summarization_task = Task(name="Custom request", is_processing=True, state="Processing", transcript=transcript, processed_filename=processed_filename)
        Service._task_manager.set_current_task(summarization_task)

        #Mock generation time
        time.sleep(10)

        #Save user_request
        create_pdf(content="Request from the user:" + user_request + '\n' + "example output", output_filename=os.path.join(os.environ["PROCESSED_FILES_PATH"], processed_filename))
 
        summarization_task = Task(name="Custom request", is_processing=False, state="Ready", transcript=transcript, processed_filename=processed_filename)
        Service._task_manager.set_current_task(summarization_task)
    
    @staticmethod
    def generate_minutes(transcript, chunk_size, output_language, participants):
        #TODO
        processed_filename = "minutes.pdf"
        summarization_task = Task(name="Meeting minutes", is_processing=True, state="Processing", transcript=transcript, processed_filename=processed_filename)
        Service._task_manager.set_current_task(summarization_task)

        #Mock generation time
        time.sleep(10)

        #Save user_request
        create_pdf(content="example output", output_filename=os.path.join(os.environ["PROCESSED_FILES_PATH"], processed_filename))
 
        summarization_task = Task(name="Meeting minutes", is_processing=False, state="Ready", transcript=transcript, processed_filename=processed_filename)
        Service._task_manager.set_current_task(summarization_task)

    @staticmethod
    def generate_action_items(transcript, chunk_size, output_language, participants):
        #TODO
        processed_filename = "action_items.pdf"
        summarization_task = Task(name="Action items", is_processing=True, state="Processing", transcript=transcript, processed_filename=processed_filename)
        Service._task_manager.set_current_task(summarization_task)

        #Mock generation time
        time.sleep(10)

        #Save user_request
        create_pdf(content="example output", output_filename=os.path.join(os.environ["PROCESSED_FILES_PATH"], processed_filename))
 
        summarization_task = Task(name="Action items", is_processing=False, state="Ready", transcript=transcript, processed_filename=processed_filename)
        Service._task_manager.set_current_task(summarization_task)