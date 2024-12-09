from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, Response
from .controllers import controller
from .controllers import sse_controller
from starlette.responses import FileResponse 
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(controller.router)
app.include_router(sse_controller.router)

app.mount("/", StaticFiles(directory=os.environ["FRONTEND_PATH"], html = True), name="frontend")

#TODO: first run: generate rag databases

def custom_openapi_message():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API",
        version="1.0",
        summary="API documentation",
        description="All the routes are specified below, with their respective **OpenAPI** schemas",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi_message