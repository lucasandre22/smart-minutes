from fastapi import Request
from fastapi import APIRouter
from fastapi import UploadFile
from ..schemas import *
from ..services.service import Service

router = APIRouter(
    prefix="/api/v1"
)

@router.get('/list/models')
async def models(req: Request):
    return Service.get_models()

@router.get('/list/transcriptions')
async def transcriptions(req: Request):
    return Service.list_transcriptions()

@router.get('/list/documents')
async def documents(req: Request):
    return Service.list_documents()

@router.post('/upload/transcription')
async def upload_transcription(file: UploadFile):
    try:
        contents = await file.read()
    except Exception as e:
        return {'error': 'Error processing the request, please try again.', 'details': "", 'response': 'Error processing the request, please try again.'}
    return {"filename": file.filename}

@router.post('/upload/document')
async def upload_document(file: UploadFile):
    return {"filename": file.filename}

@router.post('/send')
async def send(req: Request):
    body = await req.json()
    response = ""
    try:
        response = Service.send(body)
    except Exception as e:
        response = {'error': 'Error processing the request, please try again.', 'details': "", 'response': 'Error processing the request, please try again.'}
    return response