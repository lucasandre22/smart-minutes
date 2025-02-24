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
from core.config import CONFIG
from langchain_community.llms import Ollama
from summarization.refine import SummarizationRefine
from minutes.refine import MinutesRefine
from custom_request.refine import CustomRequestRefine
from scripts.vvt_cleaner import clear_vtt_file_content
from action_items.action_items import ActionItems
from rag.database.docs_rag_database import DocumentRagDatabase
from rag.document_loader import PdfDocumentLoader
import threading

OLLAMA_API_ADDRESS = os.getenv("OLLAMA_API_ADDRESS")

class Service():
    _task_manager: TaskManager = TaskManager()
    _rag_database: DocumentRagDatabase = DocumentRagDatabase(os.getenv("DOCUMENT_DATABASE_PATH"))
    
    @staticmethod
    def update_db(new_file):
        print("Updating rag database with document file: ", new_file)
        document_file = PdfDocumentLoader(new_file, 1024, True)

        # if directory exists but empty, create a new db
        if os.path.exists(os.getenv("DOCUMENT_DATABASE_PATH")) and len(os.listdir(os.getenv("DOCUMENT_DATABASE_PATH"))) == 0:
            Service._rag_database.create_new_db(document_file)
            pass
        elif os.path.isfile(new_file):
            #TODO: include the summary of the document in a database?
            Service._rag_database.update_db(document_file.docs)
            Service._rag_database.save_local()
    
    @staticmethod
    def update_progress_percentage(time_to_run_task_seconds):
        """_summary_

        Args:
            time_to_run_task_seconds (_type_): _description_
        """
        current_data = Service._task_manager.get_current_task()
        #Average time for action items, custom and summary

        while time_to_run_task_seconds > 0 and current_data.is_processing:
            Service._task_manager.set_current_task(Task(name=current_data.name, is_processing=True, state="Processing",
                                    transcript=current_data.transcript,
                                    processed_filename=current_data.processed_filename, progress=time_to_run_task_seconds))
            time_to_run_task_seconds -= 21
            time.sleep(21)
            current_data = Service._task_manager.get_current_task()

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
        return [str(os.path.basename(file)) for file in path.rglob('*') if file.is_file() and file.suffix != '.csmt' and file.suffix != '.removed']

    @staticmethod
    async def upload_file(source_file: UploadFile, destination_path: str):
        file_path = os.path.join(destination_path, source_file.filename)
        with open(file_path, "wb") as f:
            content = await source_file.read()
            f.write(content)
        return Service.list_files(os.getenv("DOCUMENTS_PATH"))

    async def upload_transcript_file(source_file: UploadFile, destination_path: str):
        file_path: str = os.path.join(destination_path, source_file.filename)
        with open(file_path, "wb") as f:
            content = await source_file.read()
            f.write(content)
            f.close()
        if file_path.endswith(".vtt"):
            cleaned_file = file_path.replace(".vtt", ".csmt")
            with open(cleaned_file, 'w', encoding='utf-8') as f:
                print(cleaned_file)
                cleaned_content = clear_vtt_file_content(file_path)
                f.write(cleaned_content)
                f.close()
                print()

    @staticmethod
    def download_file(file_path: str, file_name: str):
        return FileResponse(path=file_path, filename=file_name, media_type="application/octet-stream")

    @staticmethod
    def remove_file(file_path: UploadFile):
        if os.path.exists(file_path):
            #Do not remove document files!
            os.rename(file_path, file_path + '.removed')
            #os.remove(file_path)
    
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
    def generate_summary(transcript: str, chunk_size, summarization_language, enable_evalluation_system):
        try:
            now = datetime.now()
            formatted_date = now.strftime("%y-%m-%d-%H-%M")
            processed_filename = transcript.split(".")[0] + "-" + formatted_date + "-summary.pdf"
            
            chunk_size = 1024

            summarization_task = Task(name="Summarization", is_processing=True, state="Processing", transcript=transcript, processed_filename=processed_filename)
            Service._task_manager.set_current_task(summarization_task)

            llm = Ollama(
                model=CONFIG.model,
                verbose=True,
                temperature=CONFIG.temperature
            )

            if transcript.endswith(".vtt"):
                transcript = transcript.replace(".vtt", ".csmt")
            transcript_path = os.path.join(os.environ["TRANSCRIPTS_PATH"], transcript)

            summarization_refine = SummarizationRefine(llm)
            docs = summarization_refine.chunk_file_into_documents(transcript_path, chunk_size)
            
            time_to_generate_summary_seconds = len(docs) * 21

            progress_thread = threading.Thread(target=Service.update_progress_percentage, args=[time_to_generate_summary_seconds])
            progress_thread.start()

            result = summarization_refine.invoke(docs)
            content = result["output_text"]

            create_pdf(content=content, output_filename=os.path.join(os.environ["PROCESSED_FILES_PATH"], processed_filename))

            summarization_task = Task(name="Summarization", is_processing=False, state="Ready", transcript=transcript, processed_filename=processed_filename)
            Service._task_manager.set_current_task(summarization_task)
        except Exception as e:
            Service._task_manager.clear_current_task()
            raise e
    
    @staticmethod
    def generate_custom_request(transcript, chunk_size, output_language, user_request):
        try:
            now = datetime.now()
            formatted_date = now.strftime("%y-%m-%d-%H-%M")
            processed_filename = transcript.split(".")[0] + "-" + formatted_date + "-custom.pdf"
            #TODO: remove this
            chunk_size = 1024

            task = Task(name="Custom request", is_processing=True, state="Processing", transcript=transcript, processed_filename=processed_filename)
            Service._task_manager.set_current_task(task)

            llm = Ollama(
                model=CONFIG.model,
                verbose=True,
                temperature=CONFIG.temperature,
            )
            if transcript.endswith(".vtt"):
                transcript = transcript.replace(".vtt", ".csmt")

            transcript_path = os.path.join(os.environ["TRANSCRIPTS_PATH"], transcript)

            summarization_refine = CustomRequestRefine(llm, user_request)
            docs = summarization_refine.chunk_file_into_documents(transcript_path, chunk_size)
            
            time_to_generate_custom_seconds = len(docs) * 21
            
            progress_thread = threading.Thread(target=Service.update_progress_percentage, args=[time_to_generate_custom_seconds])
            progress_thread.start()

            result = summarization_refine.invoke(docs)
            content = result["output_text"]

            #Save user_request
            create_pdf(content="Request from the user:" + user_request + '\n\nContent:\n' + content, output_filename=os.path.join(os.environ["PROCESSED_FILES_PATH"], processed_filename))
    
            task = Task(name="Custom request", is_processing=False, state="Ready", transcript=transcript, processed_filename=processed_filename)
            Service._task_manager.set_current_task(task)
        except Exception as e:
            Service._task_manager.clear_current_task()
            raise e
    
    @staticmethod
    def generate_minutes(transcript: str, chunk_size, output_language, participants):
        try:
            now = datetime.now()
            formatted_date = now.strftime("%y-%m-%d-%H-%M")
            processed_filename = transcript.split(".")[0] + "-" + formatted_date + "-minutes.pdf"
            chunk_size = 1024
            task = Task(name="Meeting minutes", is_processing=True, state="Processing", transcript=transcript, processed_filename=processed_filename)
            Service._task_manager.set_current_task(task)

            llm = Ollama(
                model=CONFIG.model,
                verbose=True,
                temperature=CONFIG.temperature,
            )

            if transcript.endswith(".vtt"):
                transcript = transcript.replace(".vtt", ".csmt")

            transcript_path = os.path.join(os.environ["TRANSCRIPTS_PATH"], transcript)
            #Calculate time to run:
            summarization_refine = MinutesRefine(llm, participants)
            docs = summarization_refine.chunk_file_into_documents(transcript_path, chunk_size)
            time_to_generate_minutes_seconds = len(docs) * 21 * 2
            progress_thread = threading.Thread(target=Service.update_progress_percentage, args=[time_to_generate_minutes_seconds])
            progress_thread.start()

            from api.services.minutes_service import MinutesService
            content = MinutesService.generate_minutes(transcript_path, participants)

            #Save user_request
            create_pdf(content=content, output_filename=os.path.join(os.environ["PROCESSED_FILES_PATH"], processed_filename))
    
            task = Task(name="Meeting minutes", is_processing=False, state="Ready", transcript=transcript, processed_filename=processed_filename)
            Service._task_manager.set_current_task(task)
        except Exception as e:
            Service._task_manager.clear_current_task()
            raise e

    @staticmethod
    def generate_action_items(transcript, chunk_size, output_language, participants):
        try:
            now = datetime.now()
            formatted_date = now.strftime("%y-%m-%d-%H-%M")
            processed_filename = transcript.split(".")[0] + "-" + formatted_date + "-action-items.pdf"
            chunk_size = 1024
            task = Task(name="Action items", is_processing=True, state="Processing", transcript=transcript, processed_filename=processed_filename)
            Service._task_manager.set_current_task(task)

            llm = Ollama(
                model=CONFIG.model,
                verbose=True,
                temperature=CONFIG.temperature,
            )

            if transcript.endswith(".vtt"):
                transcript = transcript.replace(".vtt", ".csmt")

            transcript_path = os.path.join(os.environ["TRANSCRIPTS_PATH"], transcript)

            #get and send participants!!!

            action_items = ActionItems(llm)
            docs = action_items.chunk_file_into_documents(transcript_path, chunk_size)

            #TODO: check if ok
            time_to_generate_action_items_seconds = len(docs) * 21
            
            progress_thread = threading.Thread(target=Service.update_progress_percentage, args=[time_to_generate_action_items_seconds])
            progress_thread.start()

            result = action_items.invoke(docs)
            content = result["output_text"]

            #Save user_request
            create_pdf(content=content, output_filename=os.path.join(os.environ["PROCESSED_FILES_PATH"], processed_filename))
    
            task = Task(name="Action items", is_processing=False, state="Ready", transcript=transcript, processed_filename=processed_filename)
            Service._task_manager.set_current_task(task)
        except Exception as e:
            Service._task_manager.clear_current_task()
            raise e
    
    #RAG
    @staticmethod
    async def update_rag_database(source_file: str, destination_path: str):
        file_path = os.path.join(destination_path, source_file)
        Service.update_db(file_path)

    @staticmethod
    def search_in_rag_database(query: str):
        docs = Service._rag_database.search_for_similar_docs(query)
        return docs