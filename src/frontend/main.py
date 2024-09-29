from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from .service import Service
from typing import Annotated
from fastapi import FastAPI, File, UploadFile
import urllib.parse
import json

app = FastAPI()
service = Service()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH="EXAMPLE"

# Middleware to be executed before each POST route to verify headers
def verify_post_valid_request(req):
    if "application/json" not in req.headers["Content-Type"]:
        return Response(status_code=415)
    return verify_authorization_header(req)

def verify_authorization_header(req):
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    #if auth_header != AUTH:
        #return Response(status_code=401)

    return None

@app.get('/api/models')
async def models(req: Request):
    error_response = verify_authorization_header(req)
    if error_response:
        return error_response
    return service.get_models()

@app.get('/api/transcription_files')
async def transcription_files(req: Request):
    error_response = verify_authorization_header(req)
    if error_response:
        return error_response
    return service.list_transcription_files()

@app.post('/api/upload/transcription_file')
async def create_upload_file(file: UploadFile):
    try:
        contents = await file.read()
    except Exception as e:
        response = {'error': 'Error processing the request, please try again.', 'details': "", 'response': 'Error processing the request, please try again.'}
    return {"filename": file.filename}

@app.get('/api/document_files')
async def document_files(req: Request):
    error_response = verify_authorization_header(req)
    if error_response:
        return error_response
    return service.list_document_files()

@app.post('/api/upload/document_file')
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

@app.post('/api/send')
async def send(req: Request):
    error_response = verify_post_valid_request(req)
    if error_response:
        return error_response
    body = await req.json()
    response = ""
    try:
        response = service.send(body)
    except Exception as e:
        response = {'error': 'Error processing the request, please try again.', 'details': "", 'response': 'Error processing the request, please try again.'}
    return response

def custom_openapi_csm_message():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API",
        version="1.0.0-SNAPSHOT",
        summary="API documentation",
        description="All the routes are specified below, with their respective **OpenAPI** schemas",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi_csm_message
