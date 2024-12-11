import os
from fastapi import Request, APIRouter, UploadFile, HTTPException, File, BackgroundTasks, FastAPI
from api.schemas import *
from api.services.service import Service
from core.config import *

router = APIRouter(
    prefix="/api/v1"
)

@router.get('/list/models')
async def models(req: Request):
    return Service.get_available_models()

@router.get('/list/transcripts')
async def list_transcripts(req: Request):
    return Service.list_transcriptions()

@router.get('/list/documents')
async def list_documents(req: Request):
    return Service.list_documents()

@router.get('/list/processed-files')
async def list_transcripts(req: Request):
    return Service.list_processed_files()

@router.get('/settings')
async def get_settings(req: Request):
    return Service.get_current_settings()

@router.post('/settings')
async def get_settings(req: Request):
    body = await req.json()
    return Service.set_current_settings(body)

@router.post('/upload/document')
async def upload_document(file: UploadFile):
    if file == None:
        raise HTTPException(status_code=400, detail="File not provided.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    directory = os.environ["DOCUMENTS_PATH"]
    await Service.upload_file(file, directory)
    await Service.update_rag_database(file.filename, directory)

    return {"message": f"File '{file.filename}' has been successfully uploaded"}

@router.post('/upload/transcript')
async def upload_document(file: UploadFile = File(None)):
    if file == None:
        raise HTTPException(status_code=400, detail="File not provided.")
    #if file.content_type != "application/vtt" or file.content_type != "text/plain" or file.content_type != "application/srt":
        #raise HTTPException(status_code=400, detail="Only VVT, srt or txt files are allowed.")
    directory = os.environ["TRANSCRIPTS_PATH"]
    await Service.upload_transcript_file(file, directory)
    return {"message": f"File '{file.filename}' has been successfully uploaded"}

@router.get('/download/document/{file_name}')
async def download_document(file_name: str):
    #Path to the file
    file_path = os.path.join(os.environ["DOCUMENTS_PATH"], file_name)

    #Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    return Service.download_file(file_path, file_name)

@router.get('/download/transcript/{file_name}')
async def download_transcript(file_name: str):
    #Path to the file
    file_path = os.path.join(os.environ["TRANSCRIPTS_PATH"], file_name)

    #Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    return Service.download_file(file_path, file_name)

@router.get('/download/processed-file/{file_name}')
async def download_processed_file(file_name: str):
    #Path to the file
    file_path = os.path.join(os.environ["PROCESSED_FILES_PATH"], file_name)

    #Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    return Service.download_file(file_path, file_name)

@router.post('/remove/transcript')
async def remove_transcript(req: Request):
    body = await req.json()
    filename = body["file"]
    
    file_path = os.path.join(os.environ["TRANSCRIPTS_PATH"], filename)
    print(file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    Service.remove_file(file_path)
    return {"message": f"File '{filename}' has been successfully removed"}

#TODO: avoid code repetition
@router.post('/remove/document')
async def remove_document(req: Request):
    body = await req.json()
    filename = body["file"]

    file_path = os.path.join(os.environ["DOCUMENTS_PATH"], filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    Service.remove_file(file_path)
    return {"message": f"File '{filename}' has been successfully removed"}

#TODO: avoid code repetition
@router.post('/remove/processed-file')
async def remove_processed_file(req: Request):
    body = await req.json()
    filename = body["file"]

    file_path = os.path.join(os.environ["DOCUMENTS_PATH"], filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    Service.remove_file(file_path)
    return {"message": f"File '{filename}' has been successfully removed"}

@router.post('/model/download')
async def download_model(req: Request):
    body = await req.json()
    Service.download_model(body)
    #TODO

@router.get('/generate/clear')
async def clear_generate(req: Request):
    Service.clear_current_task()

@router.get('/generate/download/{file_name}')
async def clear_generate(file_name: str):
    #Path to the file
    file_path = os.path.join(os.environ["PROCESSED_FILES_PATH"], file_name)

    #Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    Service.clear_current_task()
    
    return Service.download_file(file_path, file_name)
    
@router.post('/generate/summary', status_code=202)
async def generate_summary(req: Request, background_tasks: BackgroundTasks):
    body = await req.json()

    transcript = body["transcript"]
    chunk_size = body["chunkSize"]
    summarization_language = body["summarizationLanguage"]
    enable_evaluation_system = body["enableEvalluationSystem"]

    background_tasks.add_task(
        Service.generate_summary,
        transcript,
        chunk_size,
        summarization_language,
        enable_evaluation_system
    )

    return {"message": "ok"}

@router.post('/generate/action-items', status_code=202)
async def generate_minutes(req: Request, background_tasks: BackgroundTasks):
    body = await req.json()

    transcript = body["transcript"]
    chunk_size = body["chunkSize"]
    language = body["language"]
    participants = body["participants"]

    background_tasks.add_task(
        Service.generate_action_items,
        transcript,
        chunk_size,
        language,
        participants
    )

    return {"message": "ok"}

@router.post('/generate/minutes', status_code=202)
async def generate_minutes(req: Request, background_tasks: BackgroundTasks):
    body = await req.json()

    transcript = body["transcript"]
    chunk_size = body["chunkSize"]
    language = body["language"]
    participants = body["participants"]

    background_tasks.add_task(
        Service.generate_minutes,
        transcript,
        chunk_size,
        language,
        participants
    )

    return {"message": "ok"}

@router.post('/generate/custom', status_code=202)
async def generate_custom(req: Request, background_tasks: BackgroundTasks):
    body = await req.json()

    transcript = body["transcript"]
    chunk_size = body["chunkSize"]
    language = body["language"]
    userRequest = body["userRequest"]

    background_tasks.add_task(
        Service.generate_custom_request,
        transcript,
        chunk_size,
        language,
        userRequest
    )

    return {"message": "ok"}

@router.post('/search/documents')
async def search_documents(req: Request):
    body = await req.json()
    query = body["query"]
    return await Service.search_in_rag_database(query)